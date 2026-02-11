from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from parkly.adapters.outbound.persistence.mappers import (
    facility_to_domain,
    facility_to_orm,
    spot_to_orm,
)
from parkly.adapters.outbound.persistence.orm_models import (
    ParkingFacilityORM,
)
from parkly.application.port.logger import Logger
from parkly.domain.model.parking_facility import ParkingFacility
from parkly.domain.model.typed_ids import FacilityId
from parkly.domain.model.value_objects import Location
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


class PgParkingFacilityRepository(ParkingFacilityRepository):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        self._session_factory = session_factory
        self._logger = logger

    async def save(self, facility: ParkingFacility) -> None:
        async with self._session_factory() as session, session.begin():
            existing = await session.execute(
                select(ParkingFacilityORM)
                .options(selectinload(ParkingFacilityORM.spots))
                .where(ParkingFacilityORM.ulid == facility.id.value)
            )
            row: ParkingFacilityORM | None = existing.scalar_one_or_none()

            if row is not None:
                row.name = facility.name.value
                row.latitude = facility.location.latitude
                row.longitude = facility.location.longitude
                row.address = facility.location.address
                row.facility_type = facility.facility_type.value
                row.access_control = facility.access_control.value
                row.total_capacity = facility.total_capacity.value

                domain_spot_ulids = {s.id.value for s in facility.spots}
                existing_spot_ulids = {s.ulid for s in row.spots}

                for orm_spot in list(row.spots):
                    if orm_spot.ulid not in domain_spot_ulids:
                        await session.delete(orm_spot)

                for orm_spot in row.spots:
                    if orm_spot.ulid in domain_spot_ulids:
                        domain_spot = next(
                            s for s in facility.spots if s.id.value == orm_spot.ulid
                        )
                        orm_spot.spot_number = domain_spot.spot_number.value
                        orm_spot.spot_type = domain_spot.spot_type.value
                        orm_spot.status = domain_spot.status.value

                for domain_spot in facility.spots:
                    if domain_spot.id.value not in existing_spot_ulids:
                        new_orm = spot_to_orm(domain_spot, row.pk)
                        session.add(new_orm)
            else:
                orm = facility_to_orm(facility)
                session.add(orm)
                await session.flush()
                for domain_spot in facility.spots:
                    spot_orm = spot_to_orm(domain_spot, orm.pk)
                    session.add(spot_orm)

        self._logger.debug(
            "Facility saved",
            extra={"facility_id": facility.id.value},
        )

    async def find_by_id(self, id: FacilityId) -> ParkingFacility | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ParkingFacilityORM)
                .options(selectinload(ParkingFacilityORM.spots))
                .where(ParkingFacilityORM.ulid == id.value)
            )
            row = result.scalar_one_or_none()

        found = row is not None
        self._logger.debug(
            "Facility lookup",
            extra={"facility_id": id.value, "found": found},
        )
        if row is None:
            return None
        return facility_to_domain(row)

    async def find_by_location(
        self, location: Location, radius: Decimal
    ) -> list[ParkingFacility]:
        lat = float(location.latitude)
        lng = float(location.longitude)
        radius_km = float(radius)

        haversine_sql = text("""
            SELECT pk FROM parking_facilities
            WHERE (
                6371.0 * acos(
                    LEAST(1.0, GREATEST(-1.0,
                        cos(radians(:lat)) * cos(radians(latitude))
                        * cos(radians(longitude) - radians(:lng))
                        + sin(radians(:lat)) * sin(radians(latitude))
                    ))
                )
            ) <= :radius
        """)

        async with self._session_factory() as session:
            pk_result = await session.execute(
                haversine_sql, {"lat": lat, "lng": lng, "radius": radius_km}
            )
            pks = [row[0] for row in pk_result.fetchall()]

            if not pks:
                self._logger.debug(
                    "Facility location search",
                    extra={
                        "latitude": str(location.latitude),
                        "longitude": str(location.longitude),
                        "radius_km": str(radius),
                        "found": 0,
                    },
                )
                return []

            result = await session.execute(
                select(ParkingFacilityORM)
                .options(selectinload(ParkingFacilityORM.spots))
                .where(ParkingFacilityORM.pk.in_(pks))
            )
            rows = result.scalars().all()

        facilities = [facility_to_domain(r) for r in rows]
        self._logger.debug(
            "Facility location search",
            extra={
                "latitude": str(location.latitude),
                "longitude": str(location.longitude),
                "radius_km": str(radius),
                "found": len(facilities),
            },
        )
        return facilities

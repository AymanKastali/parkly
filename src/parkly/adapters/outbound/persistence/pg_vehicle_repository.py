from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from parkly.adapters.outbound.persistence.mappers import (
    vehicle_to_domain,
    vehicle_to_orm,
)
from parkly.adapters.outbound.persistence.orm_models import VehicleORM
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import OwnerId, VehicleId
from parkly.domain.model.value_objects import LicensePlate
from parkly.domain.model.vehicle import Vehicle
from parkly.domain.port.vehicle_repository import VehicleRepository


class PgVehicleRepository(VehicleRepository):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        self._session_factory = session_factory
        self._logger = logger

    async def save(self, vehicle: Vehicle) -> None:
        async with self._session_factory() as session, session.begin():
            result = await session.execute(
                select(VehicleORM).where(VehicleORM.ulid == vehicle.id.value)
            )
            row: VehicleORM | None = result.scalar_one_or_none()

            if row is not None:
                row.owner_ulid = vehicle.owner_id.value
                row.license_plate_value = vehicle.license_plate.value
                row.license_plate_region = vehicle.license_plate.region
                row.vehicle_type = vehicle.vehicle_type.value
                row.is_ev = vehicle.is_ev
            else:
                orm = vehicle_to_orm(vehicle)
                session.add(orm)

        self._logger.debug(
            "Vehicle saved",
            extra={"vehicle_id": vehicle.id.value},
        )

    async def find_by_id(self, id: VehicleId) -> Vehicle | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(VehicleORM).where(VehicleORM.ulid == id.value)
            )
            row = result.scalar_one_or_none()

        self._logger.debug(
            "Vehicle lookup",
            extra={"vehicle_id": id.value, "found": row is not None},
        )
        if row is None:
            return None
        return vehicle_to_domain(row)

    async def find_by_owner(self, owner_id: OwnerId) -> list[Vehicle]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(VehicleORM).where(VehicleORM.owner_ulid == owner_id.value)
            )
            rows = result.scalars().all()

        vehicles = [vehicle_to_domain(r) for r in rows]
        self._logger.debug(
            "Vehicle owner search",
            extra={"owner_id": owner_id.value, "found": len(vehicles)},
        )
        return vehicles

    async def find_by_license_plate(self, plate: LicensePlate) -> Vehicle | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(VehicleORM).where(
                    VehicleORM.license_plate_value == plate.value,
                    VehicleORM.license_plate_region == plate.region,
                )
            )
            row = result.scalar_one_or_none()

        self._logger.debug(
            "Vehicle plate lookup",
            extra={
                "plate": plate.formatted(),
                "found": row is not None,
            },
        )
        if row is None:
            return None
        return vehicle_to_domain(row)

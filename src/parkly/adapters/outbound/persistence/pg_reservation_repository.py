from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from parkly.adapters.outbound.persistence.mappers import (
    reservation_to_domain,
    reservation_to_orm,
)
from parkly.adapters.outbound.persistence.orm_models import ReservationORM
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import ReservationId, SpotId, VehicleId
from parkly.domain.model.reservation import Reservation
from parkly.domain.model.value_objects import TimeSlot
from parkly.domain.port.reservation_repository import ReservationRepository


class PgReservationRepository(ReservationRepository):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        self._session_factory = session_factory
        self._logger = logger

    async def save(self, reservation: Reservation) -> None:
        async with self._session_factory() as session, session.begin():
            result = await session.execute(
                select(ReservationORM).where(
                    ReservationORM.ulid == reservation.id.value
                )
            )
            row: ReservationORM | None = result.scalar_one_or_none()

            if row is not None:
                row.facility_ulid = reservation.facility_id.value
                row.spot_ulid = reservation.spot_id.value
                row.vehicle_ulid = reservation.vehicle_id.value
                row.time_slot_start = reservation.time_slot.start
                row.time_slot_end = reservation.time_slot.end
                row.status = reservation.status.value
                row.cost_amount = reservation.total_cost.amount
                row.cost_currency = reservation.total_cost.currency.code
                row.created_at = reservation.created_at
            else:
                orm = reservation_to_orm(reservation)
                session.add(orm)

        self._logger.debug(
            "Reservation saved",
            extra={"reservation_id": reservation.id.value},
        )

    async def find_by_id(self, id: ReservationId) -> Reservation | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReservationORM).where(ReservationORM.ulid == id.value)
            )
            row = result.scalar_one_or_none()

        self._logger.debug(
            "Reservation lookup",
            extra={"reservation_id": id.value, "found": row is not None},
        )
        if row is None:
            return None
        return reservation_to_domain(row)

    async def find_by_spot_and_time(
        self, spot_id: SpotId, time_slot: TimeSlot
    ) -> list[Reservation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReservationORM).where(
                    ReservationORM.spot_ulid == spot_id.value,
                    ReservationORM.time_slot_start < time_slot.end,
                    ReservationORM.time_slot_end > time_slot.start,
                )
            )
            rows = result.scalars().all()

        reservations = [reservation_to_domain(r) for r in rows]
        self._logger.debug(
            "Reservation spot+time search",
            extra={
                "spot_id": spot_id.value,
                "start": str(time_slot.start),
                "end": str(time_slot.end),
                "found": len(reservations),
            },
        )
        return reservations

    async def find_by_vehicle(self, vehicle_id: VehicleId) -> list[Reservation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReservationORM).where(
                    ReservationORM.vehicle_ulid == vehicle_id.value
                )
            )
            rows = result.scalars().all()

        reservations = [reservation_to_domain(r) for r in rows]
        self._logger.debug(
            "Reservation vehicle search",
            extra={"vehicle_id": vehicle_id.value, "found": len(reservations)},
        )
        return reservations

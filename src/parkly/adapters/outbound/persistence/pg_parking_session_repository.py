from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from parkly.adapters.outbound.persistence.mappers import (
    session_to_domain,
    session_to_orm,
)
from parkly.adapters.outbound.persistence.orm_models import ParkingSessionORM
from parkly.application.port.logger import Logger
from parkly.domain.model.parking_session import ParkingSession
from parkly.domain.model.typed_ids import SessionId, SpotId, VehicleId
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


class PgParkingSessionRepository(ParkingSessionRepository):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        self._session_factory = session_factory
        self._logger = logger

    async def save(self, session: ParkingSession) -> None:
        async with self._session_factory() as db_session, db_session.begin():
            result = await db_session.execute(
                select(ParkingSessionORM).where(
                    ParkingSessionORM.ulid == session.id.value
                )
            )
            row: ParkingSessionORM | None = result.scalar_one_or_none()

            if row is not None:
                row.reservation_ulid = (
                    session.reservation_id.value if session.reservation_id else None
                )
                row.facility_ulid = session.facility_id.value
                row.spot_ulid = session.spot_id.value
                row.vehicle_ulid = session.vehicle_id.value
                row.entry_time = session.entry_time
                row.exit_time = session.exit_time
                row.cost_amount = session.total_cost.amount
                row.cost_currency = session.total_cost.currency.code
            else:
                orm = session_to_orm(session)
                db_session.add(orm)

        self._logger.debug(
            "Session saved",
            extra={"session_id": session.id.value},
        )

    async def find_by_id(self, id: SessionId) -> ParkingSession | None:
        async with self._session_factory() as db_session:
            result = await db_session.execute(
                select(ParkingSessionORM).where(ParkingSessionORM.ulid == id.value)
            )
            row = result.scalar_one_or_none()

        self._logger.debug(
            "Session lookup",
            extra={"session_id": id.value, "found": row is not None},
        )
        if row is None:
            return None
        return session_to_domain(row)

    async def find_active_by_spot(self, spot_id: SpotId) -> ParkingSession | None:
        async with self._session_factory() as db_session:
            result = await db_session.execute(
                select(ParkingSessionORM).where(
                    ParkingSessionORM.spot_ulid == spot_id.value,
                    ParkingSessionORM.exit_time.is_(None),
                )
            )
            row = result.scalar_one_or_none()

        self._logger.debug(
            "Active session spot lookup",
            extra={"spot_id": spot_id.value, "found": row is not None},
        )
        if row is None:
            return None
        return session_to_domain(row)

    async def find_by_vehicle(self, vehicle_id: VehicleId) -> list[ParkingSession]:
        async with self._session_factory() as db_session:
            result = await db_session.execute(
                select(ParkingSessionORM).where(
                    ParkingSessionORM.vehicle_ulid == vehicle_id.value
                )
            )
            rows = result.scalars().all()

        sessions = [session_to_domain(r) for r in rows]
        self._logger.debug(
            "Session vehicle search",
            extra={"vehicle_id": vehicle_id.value, "found": len(sessions)},
        )
        return sessions

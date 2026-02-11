from parkly.application.port.logger import Logger
from parkly.domain.model.parking_session import ParkingSession
from parkly.domain.model.typed_ids import SessionId, SpotId, VehicleId
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


class InMemoryParkingSessionRepository(ParkingSessionRepository):
    def __init__(self, logger: Logger) -> None:
        self._store: dict[SessionId, ParkingSession] = {}
        self._logger: Logger = logger

    async def save(self, session: ParkingSession) -> None:
        self._store[session.id] = session
        self._logger.debug(
            "Session saved",
            extra={"session_id": str(session.id.value)},
        )

    async def find_by_id(self, id: SessionId) -> ParkingSession | None:
        result: ParkingSession | None = self._store.get(id)
        self._logger.debug(
            "Session lookup",
            extra={"session_id": str(id.value), "found": result is not None},
        )
        return result

    async def find_active_by_spot(self, spot_id: SpotId) -> ParkingSession | None:
        for session in self._store.values():
            if session.spot_id == spot_id and session.is_active:
                self._logger.debug(
                    "Active session found for spot",
                    extra={
                        "spot_id": str(spot_id.value),
                        "session_id": str(session.id.value),
                    },
                )
                return session
        self._logger.debug(
            "No active session for spot",
            extra={"spot_id": str(spot_id.value)},
        )
        return None

    async def find_by_vehicle(self, vehicle_id: VehicleId) -> list[ParkingSession]:
        results: list[ParkingSession] = [
            session
            for session in self._store.values()
            if session.vehicle_id == vehicle_id
        ]
        self._logger.debug(
            "Session vehicle search",
            extra={"vehicle_id": str(vehicle_id.value), "found": len(results)},
        )
        return results

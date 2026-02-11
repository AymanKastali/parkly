from dataclasses import dataclass

from parkly.application.dto.session_dto import SessionDTO
from parkly.application.port.logger import Logger
from parkly.domain.model.typed_ids import VehicleId
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


@dataclass(frozen=True)
class ListVehicleSessions:
    vehicle_id: str


class ListVehicleSessionsHandler:
    def __init__(
        self,
        session_repo: ParkingSessionRepository,
        logger: Logger,
    ) -> None:
        self._session_repo = session_repo
        self._logger = logger

    async def handle(self, query: ListVehicleSessions) -> list[SessionDTO]:
        self._logger.debug(
            "Handling ListVehicleSessions",
            extra={"vehicle_id": str(query.vehicle_id)},
        )

        vehicle_id = VehicleId(value=query.vehicle_id)
        sessions = await self._session_repo.find_by_vehicle(vehicle_id)
        result = [SessionDTO.from_domain(s) for s in sessions]

        self._logger.debug(
            "ListVehicleSessions completed",
            extra={
                "vehicle_id": str(query.vehicle_id),
                "count": len(result),
            },
        )
        return result

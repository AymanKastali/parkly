from dataclasses import dataclass

from parkly.application.dto.reservation_dto import ReservationDTO
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import VehicleId
from parkly.domain.port.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class ListVehicleReservations:
    vehicle_id: str


class ListVehicleReservationsHandler:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        logger: Logger,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._logger = logger

    async def handle(self, query: ListVehicleReservations) -> list[ReservationDTO]:
        self._logger.debug(
            "Handling ListVehicleReservations",
            extra={"vehicle_id": str(query.vehicle_id)},
        )

        vehicle_id = VehicleId(value=query.vehicle_id)
        reservations = await self._reservation_repo.find_by_vehicle(vehicle_id)
        result = [ReservationDTO.from_domain(r) for r in reservations]

        self._logger.debug(
            "ListVehicleReservations completed",
            extra={
                "vehicle_id": str(query.vehicle_id),
                "count": len(result),
            },
        )
        return result

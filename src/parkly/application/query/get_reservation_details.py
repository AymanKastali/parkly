from dataclasses import dataclass

from parkly.application.dto.reservation_dto import ReservationDTO
from parkly.application.exception.exceptions import ReservationNotFoundError
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import ReservationId
from parkly.domain.port.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class GetReservationDetails:
    reservation_id: str


class GetReservationDetailsHandler:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        logger: Logger,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._logger = logger

    async def handle(self, query: GetReservationDetails) -> ReservationDTO:
        self._logger.debug(
            "Handling GetReservationDetails",
            extra={"reservation_id": str(query.reservation_id)},
        )

        reservation_id = ReservationId(value=query.reservation_id)
        reservation = await self._reservation_repo.find_by_id(reservation_id)
        if reservation is None:
            self._logger.warning(
                "Reservation not found",
                extra={"reservation_id": str(query.reservation_id)},
            )
            raise ReservationNotFoundError(reservation_id)

        self._logger.debug(
            "GetReservationDetails completed",
            extra={"reservation_id": str(query.reservation_id)},
        )
        return ReservationDTO.from_domain(reservation)

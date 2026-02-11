from dataclasses import dataclass
from datetime import datetime

from parkly.application.exception.exceptions import ReservationNotFoundError
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.typed_ids import ReservationId
from parkly.domain.port.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class ExtendReservation:
    reservation_id: str
    new_end: datetime


class ExtendReservationHandler:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: ExtendReservation) -> None:
        self._logger.info(
            "Handling ExtendReservation",
            extra={
                "reservation_id": str(command.reservation_id),
                "new_end": command.new_end.isoformat(),
            },
        )

        reservation_id = ReservationId(value=command.reservation_id)
        reservation = await self._reservation_repo.find_by_id(reservation_id)
        if reservation is None:
            self._logger.warning(
                "Reservation not found",
                extra={"reservation_id": str(command.reservation_id)},
            )
            raise ReservationNotFoundError(reservation_id)

        reservation.extend(command.new_end)

        await self._reservation_repo.save(reservation)
        await self._event_publisher.publish(reservation.collect_events())

        self._logger.info(
            "Reservation extended",
            extra={
                "reservation_id": str(command.reservation_id),
                "new_end": command.new_end.isoformat(),
            },
        )

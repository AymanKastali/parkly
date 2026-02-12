from dataclasses import dataclass

from parkly.application.exception.exceptions import ReservationNotFoundError
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.typed_ids import ReservationId
from parkly.domain.port.clock import Clock
from parkly.domain.port.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class CompleteReservation:
    reservation_id: str


class CompleteReservationHandler:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: CompleteReservation) -> None:
        self._logger.info(
            "Handling CompleteReservation",
            extra={"reservation_id": str(command.reservation_id)},
        )

        reservation_id = ReservationId(value=command.reservation_id)
        reservation = await self._reservation_repo.find_by_id(reservation_id)
        if reservation is None:
            self._logger.warning(
                "Reservation not found",
                extra={"reservation_id": str(command.reservation_id)},
            )
            raise ReservationNotFoundError(reservation_id)

        reservation.complete(occurred_at=self._clock.now())

        await self._reservation_repo.save(reservation)
        await self._event_publisher.publish(reservation.collect_events())

        self._logger.info(
            "Reservation completed",
            extra={"reservation_id": str(command.reservation_id)},
        )

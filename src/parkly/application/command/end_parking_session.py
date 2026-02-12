from dataclasses import dataclass
from decimal import Decimal

from parkly.application.exception.exceptions import SessionNotFoundError
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import SessionId
from parkly.domain.model.value_objects import Currency, Money
from parkly.domain.port.clock import Clock
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


@dataclass(frozen=True)
class EndParkingSession:
    session_id: str
    rate_per_hour_amount: Decimal
    rate_per_hour_currency: str


class EndParkingSessionHandler:
    def __init__(
        self,
        session_repo: ParkingSessionRepository,
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._session_repo = session_repo
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: EndParkingSession) -> None:
        self._logger.info(
            "Handling EndParkingSession",
            extra={"session_id": str(command.session_id)},
        )

        session_id = SessionId(value=command.session_id)
        rate_per_hour = Money(
            amount=command.rate_per_hour_amount,
            currency=Currency(code=command.rate_per_hour_currency),
        )

        session = await self._session_repo.find_by_id(session_id)
        if session is None:
            self._logger.warning(
                "Session not found",
                extra={"session_id": str(command.session_id)},
            )
            raise SessionNotFoundError(session_id)

        occurred_at = self._clock.now()
        total_cost = session.calculate_cost(rate_per_hour, occurred_at)
        session.end(total_cost, occurred_at, occurred_at=occurred_at)

        await self._session_repo.save(session)
        await self._event_publisher.publish(session.collect_events())

        self._logger.info(
            "Parking session ended",
            extra={
                "session_id": str(command.session_id),
                "total_cost": str(total_cost.amount),
            },
        )

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from parkly.application.exception.exceptions import SessionNotFoundError
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import SessionId
from parkly.domain.model.value_objects import Currency, Money
from parkly.domain.port.clock import Clock
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


@dataclass(frozen=True)
class ExtendParkingSession:
    session_id: str
    new_end: datetime
    new_total_cost_amount: Decimal
    new_total_cost_currency: str


class ExtendParkingSessionHandler:
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

    async def handle(self, command: ExtendParkingSession) -> None:
        self._logger.info(
            "Handling ExtendParkingSession",
            extra={
                "session_id": str(command.session_id),
                "new_end": command.new_end.isoformat(),
            },
        )

        session_id = SessionId(value=command.session_id)
        new_total_cost = Money(
            amount=command.new_total_cost_amount,
            currency=Currency(code=command.new_total_cost_currency),
        )

        session = await self._session_repo.find_by_id(session_id)
        if session is None:
            self._logger.warning(
                "Session not found",
                extra={"session_id": str(command.session_id)},
            )
            raise SessionNotFoundError(session_id)

        session.extend(command.new_end, new_total_cost, occurred_at=self._clock.now())

        await self._session_repo.save(session)
        await self._event_publisher.publish(session.collect_events())

        self._logger.info(
            "Parking session extended",
            extra={
                "session_id": str(command.session_id),
                "new_end": command.new_end.isoformat(),
            },
        )

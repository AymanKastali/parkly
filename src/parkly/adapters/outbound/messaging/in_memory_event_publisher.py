from typing import Any

from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.event.domain_event import DomainEvent


class InMemoryEventPublisher(EventPublisher):
    def __init__(self, logger: Logger) -> None:
        self._logger: Logger = logger
        self._published: list[DomainEvent] = []
        self._handlers: dict[type[DomainEvent], list[Any]] = {}

    def register_handler(self, event_type: type[DomainEvent], handler: object) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            event_name: str = type(event).__name__
            self._logger.info(
                f"Publishing event: {event_name}",
                extra={"event_type": event_name},
            )
            self._published.append(event)

            handlers: list[Any] = self._handlers.get(type(event), [])
            for handler in handlers:
                self._logger.debug(
                    f"Dispatching {event_name} to {type(handler).__name__}",
                )
                await handler.handle(event)

from abc import ABC, abstractmethod

from parkly.domain.event.domain_event import DomainEvent


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, events: list[DomainEvent]) -> None: ...

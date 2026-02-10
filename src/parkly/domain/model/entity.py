from dataclasses import dataclass, field

from parkly.domain.event.domain_event import DomainEvent


@dataclass
class Entity[IdT]:
    _id: IdT

    @property
    def id(self) -> IdT:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)


@dataclass
class AggregateRoot[IdT](Entity[IdT]):
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def _record_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events

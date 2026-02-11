from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from parkly.domain.exception.exceptions import RequiredFieldError


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            if getattr(self, name) is None:
                raise RequiredFieldError(type(self).__name__, name)


@dataclass(frozen=True, kw_only=True)
class EventEnvelope:
    event_id: UUID
    occurred_at: datetime
    event: DomainEvent

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            if getattr(self, name) is None:
                raise RequiredFieldError(type(self).__name__, name)

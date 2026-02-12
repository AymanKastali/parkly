from dataclasses import dataclass, fields
from datetime import datetime

from parkly.domain.exception.exceptions import RequiredFieldError


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    occurred_at: datetime

    def __post_init__(self) -> None:
        for field in fields(self):
            if getattr(self, field.name) is None:
                raise RequiredFieldError(type(self).__name__, field.name)

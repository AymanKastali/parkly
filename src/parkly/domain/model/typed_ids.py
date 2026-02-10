from dataclasses import dataclass

from parkly.domain.exception.exceptions import RequiredFieldError


@dataclass(frozen=True)
class TypedId[T]:
    value: T

    def __post_init__(self) -> None:
        if self.value is None:
            raise RequiredFieldError(type(self).__name__, "value")


@dataclass(frozen=True)
class FacilityId(TypedId): ...


@dataclass(frozen=True)
class SpotId(TypedId): ...


@dataclass(frozen=True)
class ReservationId(TypedId): ...


@dataclass(frozen=True)
class VehicleId(TypedId): ...


@dataclass(frozen=True)
class SessionId(TypedId): ...


@dataclass(frozen=True)
class OwnerId(TypedId): ...

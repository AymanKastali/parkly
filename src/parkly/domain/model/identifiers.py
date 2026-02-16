from dataclasses import dataclass

from parkly.domain.exception.exceptions import RequiredFieldError


@dataclass(frozen=True, slots=True)
class Id[T]:
    value: T

    def __post_init__(self) -> None:
        if self.value is None:
            raise RequiredFieldError(type(self).__name__, "value")

        if isinstance(self.value, str) and not self.value.strip():
            raise RequiredFieldError(type(self).__name__, "value")

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self), self.value))

    def __bool__(self) -> bool:
        return bool(self.value)


class FacilityId(Id[str]): ...


class SpotId(Id[str]): ...


class ReservationId(Id[str]): ...


class VehicleId(Id[str]): ...


class SessionId(Id[str]): ...


class OwnerId(Id[str]): ...

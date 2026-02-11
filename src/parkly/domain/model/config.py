from dataclasses import dataclass
from decimal import Decimal

from parkly.domain.exception.exceptions import (
    InvalidFreeHoursError,
    InvalidHourValueError,
    InvalidMultiplierError,
    InvalidPeakHourRangeError,
)
from parkly.domain.model.value_objects import Money


@dataclass(frozen=True)
class DynamicPricingConfig:
    surge_multiplier: Decimal

    def __post_init__(self) -> None:
        if self.surge_multiplier <= Decimal("0"):
            raise InvalidMultiplierError("surge_multiplier", self.surge_multiplier)


@dataclass(frozen=True)
class EventPricingConfig:
    event_multiplier: Decimal

    def __post_init__(self) -> None:
        if self.event_multiplier <= Decimal("0"):
            raise InvalidMultiplierError("event_multiplier", self.event_multiplier)


@dataclass(frozen=True)
class PeakHourPricingConfig:
    peak_start_hour: int
    peak_end_hour: int
    peak_multiplier: Decimal

    def __post_init__(self) -> None:
        if not (0 <= self.peak_start_hour <= 23):
            raise InvalidHourValueError("peak_start_hour", self.peak_start_hour)
        if not (0 <= self.peak_end_hour <= 23):
            raise InvalidHourValueError("peak_end_hour", self.peak_end_hour)
        if self.peak_start_hour >= self.peak_end_hour:
            raise InvalidPeakHourRangeError(self.peak_start_hour, self.peak_end_hour)
        if self.peak_multiplier <= Decimal("0"):
            raise InvalidMultiplierError("peak_multiplier", self.peak_multiplier)


@dataclass(frozen=True)
class TieredPricingConfig:
    free_hours: int

    def __post_init__(self) -> None:
        if self.free_hours < 0:
            raise InvalidFreeHoursError(self.free_hours)


@dataclass(frozen=True)
class DurationDiscountPricingConfig:
    daily_max: Money | None

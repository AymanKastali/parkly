from abc import ABC, abstractmethod
from decimal import Decimal

from parkly.domain.model.config import (
    DurationDiscountPricingConfig,
    DynamicPricingConfig,
    EventPricingConfig,
    PeakHourPricingConfig,
    TieredPricingConfig,
)
from parkly.domain.model.consts import SECONDS_PER_HOUR
from parkly.domain.model.value_objects import Money, TimeSlot


class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money: ...


class StaticPricing(PricingStrategy):
    """Flat rate per hour."""

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / SECONDS_PER_HOUR
        return base_rate.multiply(hours)


class DynamicPricing(PricingStrategy):
    """Demand-based surge pricing."""

    def __init__(self, config: DynamicPricingConfig) -> None:
        self._config = config

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / SECONDS_PER_HOUR
        return base_rate.multiply(hours * self._config.surge_multiplier)


class EventAwarePricing(PricingStrategy):
    """Premium pricing near event venues."""

    def __init__(self, config: EventPricingConfig) -> None:
        self._config = config

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / SECONDS_PER_HOUR
        return base_rate.multiply(hours * self._config.event_multiplier)


class TimeOfDayPricing(PricingStrategy):
    """Peak / off-peak tiers."""

    def __init__(self, config: PeakHourPricingConfig) -> None:
        self._config = config

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / SECONDS_PER_HOUR
        start_hour = time_slot.start.hour
        if self._config.peak_start_hour <= start_hour < self._config.peak_end_hour:
            return base_rate.multiply(hours * self._config.peak_multiplier)
        return base_rate.multiply(hours)


class TieredPricing(PricingStrategy):
    """First hour free, then graduated rates."""

    def __init__(self, config: TieredPricingConfig) -> None:
        self._config = config

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        total_hours = (
            Decimal(str(time_slot.duration().total_seconds())) / SECONDS_PER_HOUR
        )
        billable = max(
            total_hours - Decimal(str(self._config.free_hours)), Decimal("0")
        )
        return base_rate.multiply(billable)


class DurationDiscountPricing(PricingStrategy):
    """Daily max cap."""

    def __init__(self, config: DurationDiscountPricingConfig) -> None:
        self._config = config

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / SECONDS_PER_HOUR
        total = base_rate.multiply(hours)
        if (
            self._config.daily_max is not None
            and total.amount > self._config.daily_max.amount
        ):
            return self._config.daily_max
        return total

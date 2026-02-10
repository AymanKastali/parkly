from abc import ABC, abstractmethod
from decimal import Decimal

from parkly.domain.model.value_objects import Money, TimeSlot


class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money: ...


class StaticPricing(PricingStrategy):
    """Flat rate per hour."""

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / Decimal("3600")
        return base_rate.multiply(hours)


class DynamicPricing(PricingStrategy):
    """Demand-based surge pricing."""

    def __init__(self, surge_multiplier: Decimal = Decimal("1.0")) -> None:
        self._surge_multiplier = surge_multiplier

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / Decimal("3600")
        return base_rate.multiply(hours * self._surge_multiplier)


class EventAwarePricing(PricingStrategy):
    """Premium pricing near event venues."""

    def __init__(self, event_multiplier: Decimal = Decimal("2.0")) -> None:
        self._event_multiplier = event_multiplier

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / Decimal("3600")
        return base_rate.multiply(hours * self._event_multiplier)


class TimeOfDayPricing(PricingStrategy):
    """Peak / off-peak tiers."""

    def __init__(
        self,
        peak_start_hour: int = 8,
        peak_end_hour: int = 18,
        peak_multiplier: Decimal = Decimal("1.5"),
    ) -> None:
        self._peak_start_hour = peak_start_hour
        self._peak_end_hour = peak_end_hour
        self._peak_multiplier = peak_multiplier

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / Decimal("3600")
        start_hour = time_slot.start.hour
        if self._peak_start_hour <= start_hour < self._peak_end_hour:
            return base_rate.multiply(hours * self._peak_multiplier)
        return base_rate.multiply(hours)


class TieredPricing(PricingStrategy):
    """First hour free, then graduated rates."""

    def __init__(self, free_hours: int = 1) -> None:
        self._free_hours = free_hours

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        total_hours = Decimal(str(time_slot.duration().total_seconds())) / Decimal(
            "3600"
        )
        billable = max(total_hours - Decimal(str(self._free_hours)), Decimal("0"))
        return base_rate.multiply(billable)


class DurationDiscountPricing(PricingStrategy):
    """Daily max cap."""

    def __init__(self, daily_max: Money | None = None) -> None:
        self._daily_max = daily_max

    def calculate(self, time_slot: TimeSlot, base_rate: Money) -> Money:
        hours = Decimal(str(time_slot.duration().total_seconds())) / Decimal("3600")
        total = base_rate.multiply(hours)
        if self._daily_max is not None and total.amount > self._daily_max.amount:
            return self._daily_max
        return total

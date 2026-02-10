from parkly.domain.model.parking_facility import ParkingFacility
from parkly.domain.model.value_objects import Money, TimeSlot
from parkly.domain.model.vehicle import Vehicle
from parkly.domain.service.pricing_strategy import PricingStrategy


class PricingService:
    def __init__(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy

    def calculate_price(
        self,
        facility: ParkingFacility,
        time_slot: TimeSlot,
        vehicle: Vehicle,
        base_rate: Money,
    ) -> Money:
        return self._strategy.calculate(time_slot, base_rate)

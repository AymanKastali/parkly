from abc import ABC, abstractmethod
from decimal import Decimal

from parkly.domain.model.parking_facility import ParkingFacility
from parkly.domain.model.typed_ids import FacilityId
from parkly.domain.model.value_objects import Location


class ParkingFacilityRepository(ABC):
    @abstractmethod
    async def save(self, facility: ParkingFacility) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: FacilityId) -> ParkingFacility | None: ...

    @abstractmethod
    async def find_by_location(
        self, location: Location, radius: Decimal
    ) -> list[ParkingFacility]: ...

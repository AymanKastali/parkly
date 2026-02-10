from abc import ABC, abstractmethod

from parkly.domain.model.typed_ids import OwnerId, VehicleId
from parkly.domain.model.value_objects import LicensePlate
from parkly.domain.model.vehicle import Vehicle


class VehicleRepository(ABC):
    @abstractmethod
    async def save(self, vehicle: Vehicle) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: VehicleId) -> Vehicle | None: ...

    @abstractmethod
    async def find_by_owner(self, owner_id: OwnerId) -> list[Vehicle]: ...

    @abstractmethod
    async def find_by_license_plate(self, plate: LicensePlate) -> Vehicle | None: ...

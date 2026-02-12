from abc import ABC, abstractmethod

from parkly.domain.model.identifiers import ReservationId, SpotId, VehicleId
from parkly.domain.model.reservation import Reservation
from parkly.domain.model.value_objects import TimeSlot


class ReservationRepository(ABC):
    @abstractmethod
    async def save(self, reservation: Reservation) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: ReservationId) -> Reservation | None: ...

    @abstractmethod
    async def find_by_spot_and_time(
        self, spot_id: SpotId, time_slot: TimeSlot
    ) -> list[Reservation]: ...

    @abstractmethod
    async def find_by_vehicle(self, vehicle_id: VehicleId) -> list[Reservation]: ...

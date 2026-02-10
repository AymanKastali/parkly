from abc import ABC, abstractmethod

from parkly.domain.model.parking_session import ParkingSession
from parkly.domain.model.typed_ids import SessionId, SpotId, VehicleId


class ParkingSessionRepository(ABC):
    @abstractmethod
    async def save(self, session: ParkingSession) -> None: ...

    @abstractmethod
    async def find_by_id(self, id: SessionId) -> ParkingSession | None: ...

    @abstractmethod
    async def find_active_by_spot(self, spot_id: SpotId) -> ParkingSession | None: ...

    @abstractmethod
    async def find_by_vehicle(self, vehicle_id: VehicleId) -> list[ParkingSession]: ...

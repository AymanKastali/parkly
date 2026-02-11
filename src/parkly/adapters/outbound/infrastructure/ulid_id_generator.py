from ulid import ULID

from parkly.domain.model.typed_ids import (
    FacilityId,
    ReservationId,
    SessionId,
    SpotId,
    VehicleId,
)
from parkly.domain.port.id_generator import IdGenerator


class FacilityIdGenerator(IdGenerator[FacilityId]):
    def generate(self) -> FacilityId:
        return FacilityId(value=str(ULID()))


class SpotIdGenerator(IdGenerator[SpotId]):
    def generate(self) -> SpotId:
        return SpotId(value=str(ULID()))


class ReservationIdGenerator(IdGenerator[ReservationId]):
    def generate(self) -> ReservationId:
        return ReservationId(value=str(ULID()))


class VehicleIdGenerator(IdGenerator[VehicleId]):
    def generate(self) -> VehicleId:
        return VehicleId(value=str(ULID()))


class SessionIdGenerator(IdGenerator[SessionId]):
    def generate(self) -> SessionId:
        return SessionId(value=str(ULID()))

from dataclasses import dataclass
from datetime import datetime

from parkly.domain.model.enums import SpotType
from parkly.domain.model.typed_ids import (
    FacilityId,
    OwnerId,
    ReservationId,
    SessionId,
    SpotId,
    VehicleId,
)
from parkly.domain.model.value_objects import LicensePlate, Money, TimeSlot
from parkly.domain.event.domain_event import DomainEvent

# ── ParkingFacility Events ─────────────────────────────────────


@dataclass(frozen=True)
class FacilityCreated(DomainEvent):
    facility_id: FacilityId


@dataclass(frozen=True)
class SpotAdded(DomainEvent):
    facility_id: FacilityId
    spot_id: SpotId
    spot_type: SpotType


# ── Reservation Events ─────────────────────────────────────────


@dataclass(frozen=True)
class ReservationCreated(DomainEvent):
    reservation_id: ReservationId
    facility_id: FacilityId
    spot_id: SpotId
    vehicle_id: VehicleId
    time_slot: TimeSlot


@dataclass(frozen=True)
class ReservationConfirmed(DomainEvent):
    reservation_id: ReservationId


@dataclass(frozen=True)
class ReservationCancelled(DomainEvent):
    reservation_id: ReservationId
    reason: str


# ── ParkingSession Events ──────────────────────────────────────


@dataclass(frozen=True)
class SessionStarted(DomainEvent):
    session_id: SessionId
    facility_id: FacilityId
    spot_id: SpotId
    vehicle_id: VehicleId


@dataclass(frozen=True)
class SessionExtended(DomainEvent):
    session_id: SessionId
    new_end: datetime


@dataclass(frozen=True)
class SessionEnded(DomainEvent):
    session_id: SessionId
    total_cost: Money


# ── Vehicle Events ──────────────────────────────────────────────


@dataclass(frozen=True)
class VehicleRegistered(DomainEvent):
    vehicle_id: VehicleId
    owner_id: OwnerId
    license_plate: LicensePlate

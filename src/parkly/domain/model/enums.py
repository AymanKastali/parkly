from enum import StrEnum, auto


class SpotType(StrEnum):
    STANDARD = auto()
    EV_CHARGING = auto()
    HANDICAPPED = auto()
    MOTORCYCLE = auto()
    OVERSIZED = auto()
    BICYCLE = auto()


class SpotStatus(StrEnum):
    AVAILABLE = auto()
    OCCUPIED = auto()
    RESERVED = auto()
    OUT_OF_SERVICE = auto()


class FacilityType(StrEnum):
    PUBLIC = auto()
    PRIVATE = auto()


class AccessControlMethod(StrEnum):
    LPR = auto()
    QR_CODE = auto()
    DIGITAL_PASS = auto()
    GATE_BARRIER = auto()


class ParkingCategory(StrEnum):
    HOURLY = auto()
    DAILY = auto()
    MONTHLY = auto()
    EVENT = auto()
    AIRPORT = auto()
    VALET = auto()
    PEER_TO_PEER = auto()


class ReservationStatus(StrEnum):
    PENDING = auto()
    CONFIRMED = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class VehicleType(StrEnum):
    CAR = auto()
    MOTORCYCLE = auto()
    TRUCK = auto()
    BICYCLE = auto()

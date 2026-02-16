from parkly.domain.model.identifiers import (
    FacilityId,
    ReservationId,
    SessionId,
    SpotId,
    VehicleId,
)


class ApplicationError(Exception):
    code: str = "APPLICATION_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(ApplicationError):
    code: str = "NOT_FOUND"


class FacilityNotFoundError(NotFoundError):
    code: str = "FACILITY_NOT_FOUND"

    def __init__(self, facility_id: FacilityId) -> None:
        self.facility_id = facility_id
        super().__init__(f"Facility {facility_id.value} not found")


class ReservationNotFoundError(NotFoundError):
    code: str = "RESERVATION_NOT_FOUND"

    def __init__(self, reservation_id: ReservationId) -> None:
        self.reservation_id = reservation_id
        super().__init__(f"Reservation {reservation_id.value} not found")


class SessionNotFoundError(NotFoundError):
    code: str = "SESSION_NOT_FOUND"

    def __init__(self, session_id: SessionId) -> None:
        self.session_id = session_id
        super().__init__(f"Session {session_id.value} not found")


class VehicleNotFoundError(NotFoundError):
    code: str = "VEHICLE_NOT_FOUND"

    def __init__(self, vehicle_id: VehicleId) -> None:
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle {vehicle_id.value} not found")


class SpotAlreadyOccupiedError(ApplicationError):
    code: str = "SPOT_ALREADY_OCCUPIED"

    def __init__(self, spot_id: SpotId) -> None:
        self.spot_id = spot_id
        super().__init__(f"Spot {spot_id.value} is already occupied")

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────


class CreateFacilityRequest(BaseModel):
    name: str = Field(
        ..., description="Name of the parking facility", examples=["Downtown Garage"]
    )
    latitude: Decimal = Field(..., description="GPS latitude", examples=["40.7128"])
    longitude: Decimal = Field(..., description="GPS longitude", examples=["-74.0060"])
    address: str = Field(
        ..., description="Street address", examples=["123 Main St, New York, NY"]
    )
    facility_type: str = Field(
        ..., description="Type of facility: public, private", examples=["public"]
    )
    access_control: str = Field(
        ...,
        description="Access control method: lpr, qr_code, digital_pass, gate",
        examples=["lpr"],
    )
    total_capacity: int = Field(
        ..., description="Maximum number of parking spots", examples=[200]
    )


class AddSpotRequest(BaseModel):
    spot_number: str = Field(
        ...,
        description="Identifier for the spot within the facility",
        examples=["A-101"],
    )
    spot_type: str = Field(
        ...,
        description="Spot type: standard, ev_charging, handicapped, motorcycle, oversized, bicycle",
        examples=["standard"],
    )
    status: str = Field(
        "available",
        description="Initial spot status: available, occupied, reserved, out_of_service",
        examples=["available"],
    )


class CreateReservationRequest(BaseModel):
    facility_id: str = Field(
        ...,
        description="UUID of the parking facility",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    spot_id: str = Field(
        ...,
        description="UUID of the parking spot",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    vehicle_id: str = Field(
        ...,
        description="UUID of the registered vehicle",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    time_slot_start: datetime = Field(
        ...,
        description="Reservation start time (ISO 8601)",
        examples=["2026-03-01T09:00:00Z"],
    )
    time_slot_end: datetime = Field(
        ...,
        description="Reservation end time (ISO 8601)",
        examples=["2026-03-01T12:00:00Z"],
    )
    base_rate_amount: Decimal = Field(
        ..., description="Hourly rate amount", examples=["5.00"]
    )
    base_rate_currency: str = Field(
        ..., description="Currency code (ISO 4217)", examples=["USD"]
    )


class CancelReservationRequest(BaseModel):
    reason: str = Field(
        "", description="Cancellation reason", examples=["Change of plans"]
    )


class ExtendReservationRequest(BaseModel):
    new_end: datetime = Field(
        ...,
        description="New end time for the reservation (ISO 8601)",
        examples=["2026-03-01T15:00:00Z"],
    )


class StartSessionRequest(BaseModel):
    facility_id: str = Field(
        ...,
        description="UUID of the parking facility",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    spot_id: str = Field(
        ...,
        description="UUID of the parking spot",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    vehicle_id: str = Field(
        ...,
        description="UUID of the registered vehicle",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    reservation_id: str | None = Field(
        None,
        description="UUID of the associated reservation, if any",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )
    currency: str = Field(
        ..., description="Currency code for cost tracking (ISO 4217)", examples=["USD"]
    )


class ExtendSessionRequest(BaseModel):
    new_end: datetime = Field(
        ...,
        description="New expected end time (ISO 8601)",
        examples=["2026-03-01T15:00:00Z"],
    )
    new_total_cost_amount: Decimal = Field(
        ..., description="Updated total cost amount", examples=["25.00"]
    )
    new_total_cost_currency: str = Field(
        ..., description="Currency code (ISO 4217)", examples=["USD"]
    )


class EndSessionRequest(BaseModel):
    rate_per_hour_amount: Decimal = Field(
        ..., description="Hourly rate for final cost calculation", examples=["5.00"]
    )
    rate_per_hour_currency: str = Field(
        ..., description="Currency code (ISO 4217)", examples=["USD"]
    )


class RegisterVehicleRequest(BaseModel):
    owner_id: str = Field(
        ...,
        description="UUID of the vehicle owner",
        examples=["990e8400-e29b-41d4-a716-446655440004"],
    )
    license_plate_value: str = Field(
        ..., description="License plate number", examples=["ABC-1234"]
    )
    license_plate_region: str = Field(
        ..., description="License plate region/state", examples=["NY"]
    )
    vehicle_type: str = Field(
        ...,
        description="Vehicle type: car, motorcycle, truck, bicycle",
        examples=["car"],
    )
    is_ev: bool = Field(
        ..., description="Whether the vehicle is electric", examples=[False]
    )


# ── Response Models ───────────────────────────────────────────


class CreatedResponse(BaseModel):
    id: str = Field(
        ...,
        description="UUID of the created resource",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error class name", examples=["NotFoundError"])
    detail: str = Field(
        ..., description="Human-readable error message", examples=["Facility not found"]
    )


class SpotResponse(BaseModel):
    spot_id: str = Field(..., description="UUID of the parking spot")
    spot_number: str = Field(
        ..., description="Spot identifier within the facility", examples=["A-101"]
    )
    spot_type: str = Field(..., description="Spot type", examples=["standard"])
    status: str = Field(..., description="Current spot status", examples=["available"])


class FacilityResponse(BaseModel):
    facility_id: str = Field(..., description="UUID of the facility")
    name: str = Field(..., description="Facility name", examples=["Downtown Garage"])
    latitude: str = Field(..., description="GPS latitude")
    longitude: str = Field(..., description="GPS longitude")
    address: str = Field(..., description="Street address")
    facility_type: str = Field(..., description="Facility type", examples=["public"])
    access_control: str = Field(
        ..., description="Access control method", examples=["lpr"]
    )
    total_capacity: int = Field(
        ..., description="Maximum number of spots", examples=[200]
    )
    spots: list[SpotResponse] = Field(
        ..., description="List of parking spots in this facility"
    )


class ReservationResponse(BaseModel):
    reservation_id: str = Field(..., description="UUID of the reservation")
    facility_id: str = Field(..., description="UUID of the facility")
    spot_id: str = Field(..., description="UUID of the reserved spot")
    vehicle_id: str = Field(..., description="UUID of the vehicle")
    time_slot_start: datetime = Field(..., description="Reservation start time")
    time_slot_end: datetime = Field(..., description="Reservation end time")
    status: str = Field(
        ...,
        description="Reservation status: pending, confirmed, active, completed, cancelled",
        examples=["pending"],
    )
    total_cost_amount: str = Field(
        ..., description="Total cost amount", examples=["15.00"]
    )
    total_cost_currency: str = Field(..., description="Currency code", examples=["USD"])
    created_at: datetime = Field(..., description="When the reservation was created")


class SessionResponse(BaseModel):
    session_id: str = Field(..., description="UUID of the parking session")
    reservation_id: str | None = Field(
        ..., description="UUID of the associated reservation, if any"
    )
    facility_id: str = Field(..., description="UUID of the facility")
    spot_id: str = Field(..., description="UUID of the spot")
    vehicle_id: str = Field(..., description="UUID of the vehicle")
    entry_time: datetime = Field(..., description="When the vehicle entered")
    exit_time: datetime | None = Field(
        ..., description="When the vehicle exited, null if still active"
    )
    total_cost_amount: str = Field(
        ..., description="Total cost amount", examples=["10.00"]
    )
    total_cost_currency: str = Field(..., description="Currency code", examples=["USD"])
    is_active: bool = Field(
        ..., description="Whether the session is currently active", examples=[True]
    )


class VehicleResponse(BaseModel):
    vehicle_id: str = Field(..., description="UUID of the vehicle")
    owner_id: str = Field(..., description="UUID of the owner")
    license_plate_value: str = Field(
        ..., description="License plate number", examples=["ABC-1234"]
    )
    license_plate_region: str = Field(
        ..., description="License plate region", examples=["NY"]
    )
    vehicle_type: str = Field(..., description="Vehicle type", examples=["car"])
    is_ev: bool = Field(
        ..., description="Whether the vehicle is electric", examples=[False]
    )

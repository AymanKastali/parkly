from parkly.adapters.outbound.persistence.orm_models import (
    ParkingFacilityORM,
    ParkingSessionORM,
    ParkingSpotORM,
    ReservationORM,
    VehicleORM,
)
from parkly.domain.model.enums import (
    AccessControlMethod,
    FacilityType,
    ReservationStatus,
    SpotStatus,
    SpotType,
    VehicleType,
)
from parkly.domain.model.parking_facility import ParkingFacility, ParkingSpot
from parkly.domain.model.parking_session import ParkingSession
from parkly.domain.model.reservation import Reservation
from parkly.domain.model.typed_ids import (
    FacilityId,
    OwnerId,
    ReservationId,
    SessionId,
    SpotId,
    VehicleId,
)
from parkly.domain.model.value_objects import (
    Capacity,
    Currency,
    FacilityName,
    LicensePlate,
    Location,
    Money,
    SpotNumber,
    TimeSlot,
)
from parkly.domain.model.vehicle import Vehicle


# --- ParkingSpot ---


def spot_to_orm(spot: ParkingSpot, facility_pk: int) -> ParkingSpotORM:
    return ParkingSpotORM(
        ulid=spot.id.value,
        facility_pk=facility_pk,
        spot_number=spot.spot_number.value,
        spot_type=spot.spot_type.value,
        status=spot.status.value,
    )


def spot_to_domain(orm: ParkingSpotORM) -> ParkingSpot:
    return ParkingSpot.reconstitute(
        spot_id=SpotId(value=orm.ulid),
        spot_number=SpotNumber(value=orm.spot_number),
        spot_type=SpotType(orm.spot_type),
        status=SpotStatus(orm.status),
    )


# --- ParkingFacility ---


def facility_to_orm(facility: ParkingFacility) -> ParkingFacilityORM:
    return ParkingFacilityORM(
        ulid=facility.id.value,
        name=facility.name.value,
        latitude=facility.location.latitude,
        longitude=facility.location.longitude,
        address=facility.location.address,
        facility_type=facility.facility_type.value,
        access_control=facility.access_control.value,
        total_capacity=facility.total_capacity.value,
    )


def facility_to_domain(orm: ParkingFacilityORM) -> ParkingFacility:
    spots = [spot_to_domain(s) for s in orm.spots]
    return ParkingFacility.reconstitute(
        facility_id=FacilityId(value=orm.ulid),
        name=FacilityName(value=orm.name),
        location=Location(
            latitude=orm.latitude,
            longitude=orm.longitude,
            address=orm.address,
        ),
        facility_type=FacilityType(orm.facility_type),
        access_control=AccessControlMethod(orm.access_control),
        total_capacity=Capacity(value=orm.total_capacity),
        spots=spots,
    )


# --- Reservation ---


def reservation_to_orm(reservation: Reservation) -> ReservationORM:
    return ReservationORM(
        ulid=reservation.id.value,
        facility_ulid=reservation.facility_id.value,
        spot_ulid=reservation.spot_id.value,
        vehicle_ulid=reservation.vehicle_id.value,
        time_slot_start=reservation.time_slot.start,
        time_slot_end=reservation.time_slot.end,
        status=reservation.status.value,
        cost_amount=reservation.total_cost.amount,
        cost_currency=reservation.total_cost.currency.code,
        created_at=reservation.created_at,
    )


def reservation_to_domain(orm: ReservationORM) -> Reservation:
    return Reservation.reconstitute(
        reservation_id=ReservationId(value=orm.ulid),
        facility_id=FacilityId(value=orm.facility_ulid),
        spot_id=SpotId(value=orm.spot_ulid),
        vehicle_id=VehicleId(value=orm.vehicle_ulid),
        time_slot=TimeSlot(start=orm.time_slot_start, end=orm.time_slot_end),
        status=ReservationStatus(orm.status),
        total_cost=Money(
            amount=orm.cost_amount,
            currency=Currency(code=orm.cost_currency),
        ),
        created_at=orm.created_at,
    )


# --- Vehicle ---


def vehicle_to_orm(vehicle: Vehicle) -> VehicleORM:
    return VehicleORM(
        ulid=vehicle.id.value,
        owner_ulid=vehicle.owner_id.value,
        license_plate_value=vehicle.license_plate.value,
        license_plate_region=vehicle.license_plate.region,
        vehicle_type=vehicle.vehicle_type.value,
        is_ev=vehicle.is_ev,
    )


def vehicle_to_domain(orm: VehicleORM) -> Vehicle:
    return Vehicle.reconstitute(
        vehicle_id=VehicleId(value=orm.ulid),
        owner_id=OwnerId(value=orm.owner_ulid),
        license_plate=LicensePlate(
            value=orm.license_plate_value, region=orm.license_plate_region
        ),
        vehicle_type=VehicleType(orm.vehicle_type),
        is_ev=orm.is_ev,
    )


# --- ParkingSession ---


def session_to_orm(session: ParkingSession) -> ParkingSessionORM:
    return ParkingSessionORM(
        ulid=session.id.value,
        reservation_ulid=(
            session.reservation_id.value if session.reservation_id else None
        ),
        facility_ulid=session.facility_id.value,
        spot_ulid=session.spot_id.value,
        vehicle_ulid=session.vehicle_id.value,
        entry_time=session.entry_time,
        exit_time=session.exit_time,
        cost_amount=session.total_cost.amount,
        cost_currency=session.total_cost.currency.code,
    )


def session_to_domain(orm: ParkingSessionORM) -> ParkingSession:
    return ParkingSession.reconstitute(
        session_id=SessionId(value=orm.ulid),
        facility_id=FacilityId(value=orm.facility_ulid),
        spot_id=SpotId(value=orm.spot_ulid),
        vehicle_id=VehicleId(value=orm.vehicle_ulid),
        entry_time=orm.entry_time,
        total_cost=Money(
            amount=orm.cost_amount,
            currency=Currency(code=orm.cost_currency),
        ),
        reservation_id=(
            ReservationId(value=orm.reservation_ulid) if orm.reservation_ulid else None
        ),
        exit_time=orm.exit_time,
    )

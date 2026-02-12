from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from parkly.application.exception.exceptions import (
    FacilityNotFoundError,
    VehicleNotFoundError,
)
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.exception.exceptions import (
    IneligibleSpotTypeError,
    SpotAlreadyReservedError,
)
from parkly.domain.model.enums import ReservationStatus
from parkly.domain.model.identifiers import FacilityId, ReservationId, SpotId, VehicleId
from parkly.domain.model.reservation import Reservation
from parkly.domain.model.value_objects import Currency, Money, TimeSlot
from parkly.domain.port.clock import Clock
from parkly.domain.port.id_generator import IdGenerator
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository
from parkly.domain.port.reservation_repository import ReservationRepository
from parkly.domain.port.vehicle_repository import VehicleRepository
from parkly.domain.service.pricing_service import PricingService


@dataclass(frozen=True)
class CreateReservation:
    facility_id: str
    spot_id: str
    vehicle_id: str
    time_slot_start: datetime
    time_slot_end: datetime
    base_rate_amount: Decimal
    base_rate_currency: str


class CreateReservationHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        reservation_repo: ReservationRepository,
        vehicle_repo: VehicleRepository,
        id_generator: IdGenerator[ReservationId],
        pricing_service: PricingService,
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._reservation_repo = reservation_repo
        self._vehicle_repo = vehicle_repo
        self._id_generator = id_generator
        self._pricing_service = pricing_service
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: CreateReservation) -> str:
        self._logger.info(
            "Handling CreateReservation",
            extra={
                "facility_id": str(command.facility_id),
                "spot_id": str(command.spot_id),
                "vehicle_id": str(command.vehicle_id),
            },
        )

        facility_id = FacilityId(value=command.facility_id)
        spot_id = SpotId(value=command.spot_id)
        vehicle_id = VehicleId(value=command.vehicle_id)
        time_slot = TimeSlot(start=command.time_slot_start, end=command.time_slot_end)
        base_rate = Money(
            amount=command.base_rate_amount,
            currency=Currency(code=command.base_rate_currency),
        )

        facility = await self._facility_repo.find_by_id(facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found",
                extra={"facility_id": str(command.facility_id)},
            )
            raise FacilityNotFoundError(facility_id)

        vehicle = await self._vehicle_repo.find_by_id(vehicle_id)
        if vehicle is None:
            self._logger.warning(
                "Vehicle not found",
                extra={"vehicle_id": str(command.vehicle_id)},
            )
            raise VehicleNotFoundError(vehicle_id)

        spot = None
        for s in facility.spots:
            if s.id == spot_id:
                spot = s
                break

        if spot is not None:
            eligible_types = vehicle.eligible_spot_types()
            if spot.spot_type not in eligible_types:
                raise IneligibleSpotTypeError(
                    vehicle_type=vehicle.vehicle_type.value,
                    spot_type=spot.spot_type.value,
                )

        existing = await self._reservation_repo.find_by_spot_and_time(
            spot_id, time_slot
        )
        active_reservations = [
            r
            for r in existing
            if r.status
            not in (ReservationStatus.CANCELLED, ReservationStatus.COMPLETED)
        ]
        if active_reservations:
            raise SpotAlreadyReservedError(spot_identifier=str(command.spot_id))

        total_cost = self._pricing_service.calculate_price(time_slot, base_rate)

        facility.reserve_spot(spot_id)
        await self._facility_repo.save(facility)
        await self._event_publisher.publish(facility.collect_events())

        occurred_at = self._clock.now()
        reservation_id = self._id_generator.generate()
        reservation = Reservation.create(
            reservation_id=reservation_id,
            facility_id=facility_id,
            spot_id=spot_id,
            vehicle_id=vehicle_id,
            time_slot=time_slot,
            status=ReservationStatus.PENDING,
            total_cost=total_cost,
            created_at=occurred_at,
            occurred_at=occurred_at,
        )

        await self._reservation_repo.save(reservation)
        await self._event_publisher.publish(reservation.collect_events())

        self._logger.info(
            "Reservation created",
            extra={"reservation_id": str(reservation_id.value)},
        )
        return str(reservation_id.value)

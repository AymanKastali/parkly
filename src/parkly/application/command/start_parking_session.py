from dataclasses import dataclass
from decimal import Decimal

from parkly.application.exception.exceptions import (
    FacilityNotFoundError,
    SpotAlreadyOccupiedError,
)
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.parking_session import ParkingSession
from parkly.domain.model.typed_ids import (
    FacilityId,
    ReservationId,
    SessionId,
    SpotId,
    VehicleId,
)
from parkly.domain.model.value_objects import Currency, Money
from parkly.domain.port.clock import Clock
from parkly.domain.port.id_generator import IdGenerator
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


@dataclass(frozen=True)
class StartParkingSession:
    facility_id: str
    spot_id: str
    vehicle_id: str
    reservation_id: str | None
    currency: str


class StartParkingSessionHandler:
    def __init__(
        self,
        session_repo: ParkingSessionRepository,
        facility_repo: ParkingFacilityRepository,
        id_generator: IdGenerator[SessionId],
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._session_repo = session_repo
        self._facility_repo = facility_repo
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: StartParkingSession) -> str:
        self._logger.info(
            "Handling StartParkingSession",
            extra={
                "facility_id": str(command.facility_id),
                "spot_id": str(command.spot_id),
                "vehicle_id": str(command.vehicle_id),
            },
        )

        facility_id = FacilityId(value=command.facility_id)
        spot_id = SpotId(value=command.spot_id)
        vehicle_id = VehicleId(value=command.vehicle_id)
        reservation_id = (
            ReservationId(value=command.reservation_id)
            if command.reservation_id
            else None
        )
        currency = Currency(code=command.currency)

        facility = await self._facility_repo.find_by_id(facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found",
                extra={"facility_id": str(command.facility_id)},
            )
            raise FacilityNotFoundError(facility_id)

        active_session = await self._session_repo.find_active_by_spot(spot_id)
        if active_session is not None:
            raise SpotAlreadyOccupiedError(spot_id)

        occurred_at = self._clock.now()
        session_id = self._id_generator.generate()
        session = ParkingSession.create(
            session_id=session_id,
            facility_id=facility_id,
            spot_id=spot_id,
            vehicle_id=vehicle_id,
            entry_time=occurred_at,
            total_cost=Money(amount=Decimal("0"), currency=currency),
            occurred_at=occurred_at,
            reservation_id=reservation_id,
        )

        await self._session_repo.save(session)
        await self._event_publisher.publish(session.collect_events())

        self._logger.info(
            "Parking session started",
            extra={"session_id": str(session_id.value)},
        )
        return str(session_id.value)

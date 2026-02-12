from dataclasses import dataclass
from decimal import Decimal

from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.enums import AccessControlMethod, FacilityType
from parkly.domain.model.identifiers import FacilityId
from parkly.domain.model.parking_facility import ParkingFacility
from parkly.domain.model.value_objects import Capacity, FacilityName, Location
from parkly.domain.port.clock import Clock
from parkly.domain.port.id_generator import IdGenerator
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


@dataclass(frozen=True)
class CreateParkingFacility:
    name: str
    latitude: Decimal
    longitude: Decimal
    address: str
    facility_type: str
    access_control: str
    total_capacity: int


class CreateParkingFacilityHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        id_generator: IdGenerator[FacilityId],
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: CreateParkingFacility) -> str:
        self._logger.info(
            "Handling CreateParkingFacility",
            extra={
                "facility_name": command.name,
                "facility_type": command.facility_type,
            },
        )

        facility_id = self._id_generator.generate()
        name = FacilityName(value=command.name)
        location = Location(
            latitude=command.latitude,
            longitude=command.longitude,
            address=command.address,
        )
        capacity = Capacity(value=command.total_capacity)
        facility_type = FacilityType(command.facility_type)
        access_control = AccessControlMethod(command.access_control)

        occurred_at = self._clock.now()
        facility = ParkingFacility.create(
            facility_id=facility_id,
            name=name,
            location=location,
            facility_type=facility_type,
            access_control=access_control,
            total_capacity=capacity,
            occurred_at=occurred_at,
        )

        await self._facility_repo.save(facility)
        await self._event_publisher.publish(facility.collect_events())

        self._logger.info(
            "Facility created",
            extra={"facility_id": str(facility_id.value)},
        )
        return str(facility_id.value)

from dataclasses import dataclass

from parkly.application.exception.exceptions import FacilityNotFoundError
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.enums import SpotStatus, SpotType
from parkly.domain.model.identifiers import FacilityId, SpotId
from parkly.domain.model.value_objects import SpotNumber
from parkly.domain.port.clock import Clock
from parkly.domain.port.id_generator import IdGenerator
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


@dataclass(frozen=True)
class AddParkingSpot:
    facility_id: str
    spot_number: str
    spot_type: str
    status: str


class AddParkingSpotHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        id_generator: IdGenerator[SpotId],
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: AddParkingSpot) -> str:
        self._logger.info(
            "Handling AddParkingSpot",
            extra={
                "facility_id": str(command.facility_id),
                "spot_number": command.spot_number,
                "spot_type": command.spot_type,
            },
        )

        facility_id = FacilityId(value=command.facility_id)
        facility = await self._facility_repo.find_by_id(facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found",
                extra={"facility_id": str(command.facility_id)},
            )
            raise FacilityNotFoundError(facility_id)

        spot_id = self._id_generator.generate()
        spot_number = SpotNumber(value=command.spot_number)
        spot_type = SpotType(command.spot_type)
        status = SpotStatus(command.status)

        occurred_at = self._clock.now()
        facility.add_spot(
            spot_id=spot_id,
            spot_number=spot_number,
            spot_type=spot_type,
            status=status,
            occurred_at=occurred_at,
        )

        await self._facility_repo.save(facility)
        await self._event_publisher.publish(facility.collect_events())

        self._logger.info(
            "Parking spot added",
            extra={
                "facility_id": str(command.facility_id),
                "spot_id": str(spot_id.value),
            },
        )
        return str(spot_id.value)

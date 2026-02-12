from dataclasses import dataclass

from parkly.application.exception.exceptions import FacilityNotFoundError
from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.typed_ids import FacilityId, SpotId
from parkly.domain.port.clock import Clock
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


@dataclass(frozen=True)
class RemoveParkingSpot:
    facility_id: str
    spot_id: str


class RemoveParkingSpotHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: RemoveParkingSpot) -> None:
        self._logger.info(
            "Handling RemoveParkingSpot",
            extra={
                "facility_id": str(command.facility_id),
                "spot_id": str(command.spot_id),
            },
        )

        facility_id = FacilityId(value=command.facility_id)
        spot_id = SpotId(value=command.spot_id)

        facility = await self._facility_repo.find_by_id(facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found",
                extra={"facility_id": str(command.facility_id)},
            )
            raise FacilityNotFoundError(facility_id)

        occurred_at = self._clock.now()
        facility.remove_spot(spot_id, occurred_at=occurred_at)

        await self._facility_repo.save(facility)
        await self._event_publisher.publish(facility.collect_events())

        self._logger.info(
            "Parking spot removed",
            extra={
                "facility_id": str(command.facility_id),
                "spot_id": str(command.spot_id),
            },
        )

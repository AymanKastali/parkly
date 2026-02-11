from dataclasses import dataclass
from datetime import datetime

from parkly.application.dto.spot_dto import SpotDTO
from parkly.application.exception.exceptions import FacilityNotFoundError
from parkly.application.port.logger import Logger
from parkly.domain.model.enums import SpotType
from parkly.domain.model.typed_ids import FacilityId
from parkly.domain.model.value_objects import TimeSlot
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


@dataclass(frozen=True)
class FindAvailableSpots:
    facility_id: str
    time_slot_start: datetime
    time_slot_end: datetime
    spot_type: str | None = None


class FindAvailableSpotsHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._logger = logger

    async def handle(self, query: FindAvailableSpots) -> list[SpotDTO]:
        self._logger.debug(
            "Handling FindAvailableSpots",
            extra={
                "facility_id": str(query.facility_id),
                "spot_type": query.spot_type,
            },
        )

        facility_id = FacilityId(value=query.facility_id)
        time_slot = TimeSlot(start=query.time_slot_start, end=query.time_slot_end)
        spot_type = SpotType(query.spot_type) if query.spot_type else None

        facility = await self._facility_repo.find_by_id(facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found",
                extra={"facility_id": str(query.facility_id)},
            )
            raise FacilityNotFoundError(facility_id)

        available = facility.get_available_spots(
            time_slot=time_slot,
            spot_type=spot_type,
        )
        result = [SpotDTO.from_domain(s) for s in available]

        self._logger.debug(
            "FindAvailableSpots completed",
            extra={
                "facility_id": str(query.facility_id),
                "count": len(result),
            },
        )
        return result

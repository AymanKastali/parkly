from dataclasses import dataclass
from decimal import Decimal

from parkly.application.dto.facility_dto import FacilityDTO
from parkly.application.port.logger import Logger
from parkly.domain.model.value_objects import Location
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


@dataclass(frozen=True)
class FindFacilitiesByLocation:
    latitude: Decimal
    longitude: Decimal
    address: str
    radius_km: Decimal


class FindFacilitiesByLocationHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._logger = logger

    async def handle(self, query: FindFacilitiesByLocation) -> list[FacilityDTO]:
        self._logger.debug(
            "Handling FindFacilitiesByLocation",
            extra={
                "latitude": str(query.latitude),
                "longitude": str(query.longitude),
                "radius_km": str(query.radius_km),
            },
        )

        location = Location(
            latitude=query.latitude,
            longitude=query.longitude,
            address=query.address,
        )
        facilities = await self._facility_repo.find_by_location(
            location, query.radius_km
        )
        result = [FacilityDTO.from_domain(f) for f in facilities]

        self._logger.debug(
            "FindFacilitiesByLocation completed",
            extra={"count": len(result)},
        )
        return result

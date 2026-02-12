from dataclasses import dataclass

from parkly.application.dto.facility_dto import FacilityDTO
from parkly.application.exception.exceptions import FacilityNotFoundError
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import FacilityId
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


@dataclass(frozen=True)
class GetFacilityDetails:
    facility_id: str


class GetFacilityDetailsHandler:
    def __init__(
        self,
        facility_repo: ParkingFacilityRepository,
        logger: Logger,
    ) -> None:
        self._facility_repo = facility_repo
        self._logger = logger

    async def handle(self, query: GetFacilityDetails) -> FacilityDTO:
        self._logger.debug(
            "Handling GetFacilityDetails",
            extra={"facility_id": str(query.facility_id)},
        )

        facility_id = FacilityId(value=query.facility_id)
        facility = await self._facility_repo.find_by_id(facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found",
                extra={"facility_id": str(query.facility_id)},
            )
            raise FacilityNotFoundError(facility_id)

        self._logger.debug(
            "GetFacilityDetails completed",
            extra={"facility_id": str(query.facility_id)},
        )
        return FacilityDTO.from_domain(facility)

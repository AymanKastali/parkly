from decimal import Decimal

from parkly.application.port.logger import Logger
from parkly.domain.model.parking_facility import ParkingFacility
from parkly.domain.model.typed_ids import FacilityId
from parkly.domain.model.value_objects import Location
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository


class InMemoryParkingFacilityRepository(ParkingFacilityRepository):
    def __init__(self, logger: Logger) -> None:
        self._store: dict[FacilityId, ParkingFacility] = {}
        self._logger: Logger = logger

    async def save(self, facility: ParkingFacility) -> None:
        self._store[facility.id] = facility
        self._logger.debug(
            "Facility saved",
            extra={"facility_id": str(facility.id.value)},
        )

    async def find_by_id(self, id: FacilityId) -> ParkingFacility | None:
        result: ParkingFacility | None = self._store.get(id)
        self._logger.debug(
            "Facility lookup",
            extra={"facility_id": str(id.value), "found": result is not None},
        )
        return result

    async def find_by_location(
        self, location: Location, radius: Decimal
    ) -> list[ParkingFacility]:
        results: list[ParkingFacility] = [
            facility
            for facility in self._store.values()
            if facility.location.distance_to(location) <= radius
        ]
        self._logger.debug(
            "Facility location search",
            extra={
                "latitude": str(location.latitude),
                "longitude": str(location.longitude),
                "radius_km": str(radius),
                "found": len(results),
            },
        )
        return results

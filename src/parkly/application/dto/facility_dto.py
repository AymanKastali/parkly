from dataclasses import dataclass

from parkly.domain.model.parking_facility import ParkingFacility
from parkly.application.dto.spot_dto import SpotDTO


@dataclass(frozen=True)
class FacilityDTO:
    facility_id: str
    name: str
    latitude: str
    longitude: str
    address: str
    facility_type: str
    access_control: str
    total_capacity: int
    spots: list[SpotDTO]

    @staticmethod
    def from_domain(facility: ParkingFacility) -> "FacilityDTO":
        return FacilityDTO(
            facility_id=str(facility.id.value),
            name=str(facility.name),
            latitude=str(facility.location.latitude),
            longitude=str(facility.location.longitude),
            address=facility.location.address,
            facility_type=facility.facility_type.value,
            access_control=facility.access_control.value,
            total_capacity=facility.total_capacity.value,
            spots=[SpotDTO.from_domain(s) for s in facility.spots],
        )

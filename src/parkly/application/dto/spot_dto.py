from dataclasses import dataclass

from parkly.domain.model.parking_facility import ParkingSpot


@dataclass(frozen=True)
class SpotDTO:
    spot_id: str
    spot_number: str
    spot_type: str
    status: str

    @staticmethod
    def from_domain(spot: ParkingSpot) -> "SpotDTO":
        return SpotDTO(
            spot_id=str(spot.id.value),
            spot_number=str(spot.spot_number),
            spot_type=spot.spot_type.value,
            status=spot.status.value,
        )

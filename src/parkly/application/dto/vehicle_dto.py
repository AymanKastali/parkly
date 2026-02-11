from dataclasses import dataclass

from parkly.domain.model.vehicle import Vehicle


@dataclass(frozen=True)
class VehicleDTO:
    vehicle_id: str
    owner_id: str
    license_plate_value: str
    license_plate_region: str
    vehicle_type: str
    is_ev: bool

    @staticmethod
    def from_domain(vehicle: Vehicle) -> "VehicleDTO":
        return VehicleDTO(
            vehicle_id=str(vehicle.id.value),
            owner_id=str(vehicle.owner_id.value),
            license_plate_value=vehicle.license_plate.value,
            license_plate_region=vehicle.license_plate.region,
            vehicle_type=vehicle.vehicle_type.value,
            is_ev=vehicle.is_ev,
        )

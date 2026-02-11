from parkly.application.port.logger import Logger
from parkly.domain.model.typed_ids import OwnerId, VehicleId
from parkly.domain.model.value_objects import LicensePlate
from parkly.domain.model.vehicle import Vehicle
from parkly.domain.port.vehicle_repository import VehicleRepository


class InMemoryVehicleRepository(VehicleRepository):
    def __init__(self, logger: Logger) -> None:
        self._store: dict[VehicleId, Vehicle] = {}
        self._logger: Logger = logger

    async def save(self, vehicle: Vehicle) -> None:
        self._store[vehicle.id] = vehicle
        self._logger.debug(
            "Vehicle saved",
            extra={"vehicle_id": str(vehicle.id.value)},
        )

    async def find_by_id(self, id: VehicleId) -> Vehicle | None:
        result: Vehicle | None = self._store.get(id)
        self._logger.debug(
            "Vehicle lookup",
            extra={"vehicle_id": str(id.value), "found": result is not None},
        )
        return result

    async def find_by_owner(self, owner_id: OwnerId) -> list[Vehicle]:
        results: list[Vehicle] = [
            vehicle for vehicle in self._store.values() if vehicle.owner_id == owner_id
        ]
        self._logger.debug(
            "Vehicle owner search",
            extra={"owner_id": str(owner_id.value), "found": len(results)},
        )
        return results

    async def find_by_license_plate(self, plate: LicensePlate) -> Vehicle | None:
        for vehicle in self._store.values():
            if vehicle.license_plate == plate:
                self._logger.debug(
                    "Vehicle found by plate",
                    extra={"plate": plate.formatted()},
                )
                return vehicle
        self._logger.debug(
            "Vehicle not found by plate",
            extra={"plate": plate.formatted()},
        )
        return None

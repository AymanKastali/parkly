from dataclasses import dataclass

from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.model.enums import VehicleType
from parkly.domain.model.typed_ids import OwnerId, VehicleId
from parkly.domain.model.value_objects import LicensePlate
from parkly.domain.model.vehicle import Vehicle
from parkly.domain.port.clock import Clock
from parkly.domain.port.id_generator import IdGenerator
from parkly.domain.port.vehicle_repository import VehicleRepository


@dataclass(frozen=True)
class RegisterVehicle:
    owner_id: str
    license_plate_value: str
    license_plate_region: str
    vehicle_type: str
    is_ev: bool


class RegisterVehicleHandler:
    def __init__(
        self,
        vehicle_repo: VehicleRepository,
        id_generator: IdGenerator[VehicleId],
        clock: Clock,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._vehicle_repo = vehicle_repo
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, command: RegisterVehicle) -> str:
        self._logger.info(
            "Handling RegisterVehicle",
            extra={
                "owner_id": str(command.owner_id),
                "vehicle_type": command.vehicle_type,
            },
        )

        vehicle_id = self._id_generator.generate()
        owner_id = OwnerId(value=command.owner_id)
        license_plate = LicensePlate(
            value=command.license_plate_value,
            region=command.license_plate_region,
        )
        vehicle_type = VehicleType(command.vehicle_type)

        occurred_at = self._clock.now()
        vehicle = Vehicle.create(
            vehicle_id=vehicle_id,
            owner_id=owner_id,
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            is_ev=command.is_ev,
            occurred_at=occurred_at,
        )

        await self._vehicle_repo.save(vehicle)
        await self._event_publisher.publish(vehicle.collect_events())

        self._logger.info(
            "Vehicle registered",
            extra={"vehicle_id": str(vehicle_id.value)},
        )
        return str(vehicle_id.value)

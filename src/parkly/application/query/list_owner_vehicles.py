from dataclasses import dataclass

from parkly.application.dto.vehicle_dto import VehicleDTO
from parkly.application.port.logger import Logger
from parkly.domain.model.typed_ids import OwnerId
from parkly.domain.port.vehicle_repository import VehicleRepository


@dataclass(frozen=True)
class ListOwnerVehicles:
    owner_id: str


class ListOwnerVehiclesHandler:
    def __init__(
        self,
        vehicle_repo: VehicleRepository,
        logger: Logger,
    ) -> None:
        self._vehicle_repo = vehicle_repo
        self._logger = logger

    async def handle(self, query: ListOwnerVehicles) -> list[VehicleDTO]:
        self._logger.debug(
            "Handling ListOwnerVehicles",
            extra={"owner_id": str(query.owner_id)},
        )

        owner_id = OwnerId(value=query.owner_id)
        vehicles = await self._vehicle_repo.find_by_owner(owner_id)
        result = [VehicleDTO.from_domain(v) for v in vehicles]

        self._logger.debug(
            "ListOwnerVehicles completed",
            extra={
                "owner_id": str(query.owner_id),
                "count": len(result),
            },
        )
        return result

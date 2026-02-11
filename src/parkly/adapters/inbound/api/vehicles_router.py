from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from parkly.adapters.inbound.api.schemas import (
    CreatedResponse,
    ErrorResponse,
    RegisterVehicleRequest,
    VehicleResponse,
)
from parkly.application.command.register_vehicle import RegisterVehicle
from parkly.application.query.list_owner_vehicles import ListOwnerVehicles

if TYPE_CHECKING:
    from parkly.adapters.container import Container


def create_vehicles_router(container: Container) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/vehicles", tags=["Vehicles"])

    @router.post(
        "",
        status_code=201,
        response_model=CreatedResponse,
        summary="Register a vehicle",
        description="Register a new vehicle with license plate, type, and EV status.",
        responses={422: {"model": ErrorResponse, "description": "Validation error"}},
    )
    async def register_vehicle(body: RegisterVehicleRequest) -> CreatedResponse:
        command: RegisterVehicle = RegisterVehicle(
            owner_id=body.owner_id,
            license_plate_value=body.license_plate_value,
            license_plate_region=body.license_plate_region,
            vehicle_type=body.vehicle_type,
            is_ev=body.is_ev,
        )
        vehicle_id: str = await container.register_vehicle_handler.handle(command)
        return CreatedResponse(id=vehicle_id)

    @router.get(
        "/owner/{owner_id}",
        response_model=list[VehicleResponse],
        summary="List owner vehicles",
        description="Retrieve all vehicles registered to a specific owner.",
    )
    async def list_owner_vehicles(owner_id: str) -> list[VehicleResponse]:
        query: ListOwnerVehicles = ListOwnerVehicles(
            owner_id=owner_id,
        )
        dtos = await container.list_owner_vehicles_handler.handle(query)
        return [
            VehicleResponse(
                vehicle_id=dto.vehicle_id,
                owner_id=dto.owner_id,
                license_plate_value=dto.license_plate_value,
                license_plate_region=dto.license_plate_region,
                vehicle_type=dto.vehicle_type,
                is_ev=dto.is_ev,
            )
            for dto in dtos
        ]

    return router

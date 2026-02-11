from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from fastapi import APIRouter, Query, Response

from parkly.adapters.inbound.api.schemas import (
    AddSpotRequest,
    CreatedResponse,
    CreateFacilityRequest,
    ErrorResponse,
    FacilityResponse,
    SpotResponse,
)
from parkly.application.command.add_parking_spot import AddParkingSpot
from parkly.application.command.create_parking_facility import CreateParkingFacility
from parkly.application.command.remove_parking_spot import RemoveParkingSpot
from parkly.application.query.find_available_spots import FindAvailableSpots
from parkly.application.query.find_facilities_by_location import (
    FindFacilitiesByLocation,
)
from parkly.application.query.get_facility_details import GetFacilityDetails

if TYPE_CHECKING:
    from parkly.adapters.container import Container


def create_facilities_router(container: Container) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/facilities", tags=["Facilities"])

    @router.post(
        "",
        status_code=201,
        response_model=CreatedResponse,
        summary="Create a parking facility",
        description="Register a new parking facility with location, type, access control method, and capacity.",
        responses={422: {"model": ErrorResponse, "description": "Validation error"}},
    )
    async def create_facility(body: CreateFacilityRequest) -> CreatedResponse:
        command: CreateParkingFacility = CreateParkingFacility(
            name=body.name,
            latitude=body.latitude,
            longitude=body.longitude,
            address=body.address,
            facility_type=body.facility_type,
            access_control=body.access_control,
            total_capacity=body.total_capacity,
        )
        facility_id: str = await container.create_parking_facility_handler.handle(
            command
        )
        return CreatedResponse(id=facility_id)

    @router.get(
        "/{facility_id}",
        response_model=FacilityResponse,
        summary="Get facility details",
        description="Retrieve a parking facility by its ID, including all its spots.",
        responses={404: {"model": ErrorResponse, "description": "Facility not found"}},
    )
    async def get_facility(facility_id: str) -> FacilityResponse:
        query: GetFacilityDetails = GetFacilityDetails(
            facility_id=facility_id,
        )
        dto = await container.get_facility_details_handler.handle(query)
        return FacilityResponse(
            facility_id=dto.facility_id,
            name=dto.name,
            latitude=dto.latitude,
            longitude=dto.longitude,
            address=dto.address,
            facility_type=dto.facility_type,
            access_control=dto.access_control,
            total_capacity=dto.total_capacity,
            spots=[
                SpotResponse(
                    spot_id=s.spot_id,
                    spot_number=s.spot_number,
                    spot_type=s.spot_type,
                    status=s.status,
                )
                for s in dto.spots
            ],
        )

    @router.get(
        "",
        response_model=list[FacilityResponse],
        summary="Find facilities by location",
        description="Search for parking facilities within a radius of the given GPS coordinates.",
    )
    async def find_facilities_by_location(
        latitude: str = Query(..., description="GPS latitude", examples=["40.7128"]),
        longitude: str = Query(..., description="GPS longitude", examples=["-74.0060"]),
        address: str = Query("", description="Optional address filter"),
        radius_km: str = Query(
            "10", description="Search radius in kilometers", examples=["10"]
        ),
    ) -> list[FacilityResponse]:
        query: FindFacilitiesByLocation = FindFacilitiesByLocation(
            latitude=Decimal(latitude),
            longitude=Decimal(longitude),
            address=address,
            radius_km=Decimal(radius_km),
        )
        dtos = await container.find_facilities_by_location_handler.handle(query)
        return [
            FacilityResponse(
                facility_id=dto.facility_id,
                name=dto.name,
                latitude=dto.latitude,
                longitude=dto.longitude,
                address=dto.address,
                facility_type=dto.facility_type,
                access_control=dto.access_control,
                total_capacity=dto.total_capacity,
                spots=[
                    SpotResponse(
                        spot_id=s.spot_id,
                        spot_number=s.spot_number,
                        spot_type=s.spot_type,
                        status=s.status,
                    )
                    for s in dto.spots
                ],
            )
            for dto in dtos
        ]

    @router.post(
        "/{facility_id}/spots",
        status_code=201,
        response_model=CreatedResponse,
        summary="Add a parking spot",
        description="Add a new parking spot to an existing facility.",
        responses={
            404: {"model": ErrorResponse, "description": "Facility not found"},
            409: {"model": ErrorResponse, "description": "Capacity exceeded"},
            422: {"model": ErrorResponse, "description": "Validation error"},
        },
    )
    async def add_spot(facility_id: str, body: AddSpotRequest) -> CreatedResponse:
        command: AddParkingSpot = AddParkingSpot(
            facility_id=facility_id,
            spot_number=body.spot_number,
            spot_type=body.spot_type,
            status=body.status,
        )
        spot_id: str = await container.add_parking_spot_handler.handle(command)
        return CreatedResponse(id=spot_id)

    @router.delete(
        "/{facility_id}/spots/{spot_id}",
        status_code=204,
        summary="Remove a parking spot",
        description="Remove a parking spot from a facility.",
        responses={
            404: {"model": ErrorResponse, "description": "Facility or spot not found"},
        },
    )
    async def remove_spot(facility_id: str, spot_id: str) -> Response:
        command: RemoveParkingSpot = RemoveParkingSpot(
            facility_id=facility_id,
            spot_id=spot_id,
        )
        await container.remove_parking_spot_handler.handle(command)
        return Response(status_code=204)

    @router.get(
        "/{facility_id}/spots/available",
        response_model=list[SpotResponse],
        summary="Find available spots",
        description="Query available parking spots in a facility for a given time slot, optionally filtered by spot type.",
        responses={
            404: {"model": ErrorResponse, "description": "Facility not found"},
        },
    )
    async def find_available_spots(
        facility_id: str,
        time_slot_start: datetime = Query(
            ..., description="Start of the desired time slot (ISO 8601)"
        ),
        time_slot_end: datetime = Query(
            ..., description="End of the desired time slot (ISO 8601)"
        ),
        spot_type: str | None = Query(
            None,
            description="Filter by spot type: standard, ev_charging, handicapped, motorcycle, oversized, bicycle",
        ),
    ) -> list[SpotResponse]:
        query: FindAvailableSpots = FindAvailableSpots(
            facility_id=facility_id,
            time_slot_start=time_slot_start,
            time_slot_end=time_slot_end,
            spot_type=spot_type,
        )
        dtos = await container.find_available_spots_handler.handle(query)
        return [
            SpotResponse(
                spot_id=s.spot_id,
                spot_number=s.spot_number,
                spot_type=s.spot_type,
                status=s.status,
            )
            for s in dtos
        ]

    return router

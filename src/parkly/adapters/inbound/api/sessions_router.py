from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Response

from parkly.adapters.inbound.api.schemas import (
    CreatedResponse,
    EndSessionRequest,
    ErrorResponse,
    ExtendSessionRequest,
    SessionResponse,
    StartSessionRequest,
)
from parkly.application.command.end_parking_session import EndParkingSession
from parkly.application.command.extend_parking_session import ExtendParkingSession
from parkly.application.command.start_parking_session import StartParkingSession
from parkly.application.query.get_session_details import GetSessionDetails
from parkly.application.query.list_vehicle_sessions import ListVehicleSessions

if TYPE_CHECKING:
    from parkly.adapters.container import Container


def create_sessions_router(container: Container) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/sessions", tags=["Sessions"])

    @router.post(
        "",
        status_code=201,
        response_model=CreatedResponse,
        summary="Start a parking session",
        description="Start a new parking session when a vehicle enters a facility. Optionally link to an existing reservation.",
        responses={
            404: {"model": ErrorResponse, "description": "Facility not found"},
            409: {"model": ErrorResponse, "description": "Spot already occupied"},
        },
    )
    async def start_session(body: StartSessionRequest) -> CreatedResponse:
        reservation_id: str | None = body.reservation_id
        command: StartParkingSession = StartParkingSession(
            facility_id=body.facility_id,
            spot_id=body.spot_id,
            vehicle_id=body.vehicle_id,
            reservation_id=reservation_id,
            currency=body.currency,
        )
        session_id: str = await container.start_parking_session_handler.handle(command)
        return CreatedResponse(id=session_id)

    @router.get(
        "/vehicle/{vehicle_id}",
        response_model=list[SessionResponse],
        summary="List vehicle sessions",
        description="Retrieve all parking sessions for a specific vehicle.",
    )
    async def list_vehicle_sessions(vehicle_id: str) -> list[SessionResponse]:
        query: ListVehicleSessions = ListVehicleSessions(
            vehicle_id=vehicle_id,
        )
        dtos = await container.list_vehicle_sessions_handler.handle(query)
        return [
            SessionResponse(
                session_id=dto.session_id,
                reservation_id=dto.reservation_id,
                facility_id=dto.facility_id,
                spot_id=dto.spot_id,
                vehicle_id=dto.vehicle_id,
                entry_time=dto.entry_time,
                exit_time=dto.exit_time,
                total_cost_amount=dto.total_cost_amount,
                total_cost_currency=dto.total_cost_currency,
                is_active=dto.is_active,
            )
            for dto in dtos
        ]

    @router.get(
        "/{session_id}",
        response_model=SessionResponse,
        summary="Get session details",
        description="Retrieve a parking session by its ID.",
        responses={
            404: {"model": ErrorResponse, "description": "Session not found"},
        },
    )
    async def get_session(session_id: str) -> SessionResponse:
        query: GetSessionDetails = GetSessionDetails(
            session_id=session_id,
        )
        dto = await container.get_session_details_handler.handle(query)
        return SessionResponse(
            session_id=dto.session_id,
            reservation_id=dto.reservation_id,
            facility_id=dto.facility_id,
            spot_id=dto.spot_id,
            vehicle_id=dto.vehicle_id,
            entry_time=dto.entry_time,
            exit_time=dto.exit_time,
            total_cost_amount=dto.total_cost_amount,
            total_cost_currency=dto.total_cost_currency,
            is_active=dto.is_active,
        )

    @router.put(
        "/{session_id}/extend",
        status_code=204,
        summary="Extend a parking session",
        description="Extend an active parking session with a new end time and updated cost.",
        responses={
            404: {"model": ErrorResponse, "description": "Session not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
        },
    )
    async def extend_session(session_id: str, body: ExtendSessionRequest) -> Response:
        command: ExtendParkingSession = ExtendParkingSession(
            session_id=session_id,
            new_end=body.new_end,
            new_total_cost_amount=body.new_total_cost_amount,
            new_total_cost_currency=body.new_total_cost_currency,
        )
        await container.extend_parking_session_handler.handle(command)
        return Response(status_code=204)

    @router.put(
        "/{session_id}/end",
        status_code=204,
        summary="End a parking session",
        description="End an active parking session. Calculates the final cost based on actual duration and the provided hourly rate.",
        responses={
            404: {"model": ErrorResponse, "description": "Session not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
        },
    )
    async def end_session(session_id: str, body: EndSessionRequest) -> Response:
        command: EndParkingSession = EndParkingSession(
            session_id=session_id,
            rate_per_hour_amount=body.rate_per_hour_amount,
            rate_per_hour_currency=body.rate_per_hour_currency,
        )
        await container.end_parking_session_handler.handle(command)
        return Response(status_code=204)

    return router

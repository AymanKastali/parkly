from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Response

from parkly.adapters.inbound.api.schemas import (
    CancelReservationRequest,
    CreatedResponse,
    CreateReservationRequest,
    ErrorResponse,
    ExtendReservationRequest,
    ReservationResponse,
)
from parkly.application.command.activate_reservation import ActivateReservation
from parkly.application.command.cancel_reservation import CancelReservation
from parkly.application.command.complete_reservation import CompleteReservation
from parkly.application.command.confirm_reservation import ConfirmReservation
from parkly.application.command.create_reservation import CreateReservation
from parkly.application.command.extend_reservation import ExtendReservation
from parkly.application.query.get_reservation_details import GetReservationDetails
from parkly.application.query.list_vehicle_reservations import ListVehicleReservations

if TYPE_CHECKING:
    from parkly.adapters.container import Container


def create_reservations_router(container: Container) -> APIRouter:
    router: APIRouter = APIRouter(prefix="/reservations", tags=["Reservations"])

    @router.post(
        "",
        status_code=201,
        response_model=CreatedResponse,
        summary="Create a reservation",
        description="Reserve a parking spot for a vehicle within a specific time slot. Calculates total cost based on the base rate and duration.",
        responses={
            404: {
                "model": ErrorResponse,
                "description": "Facility or vehicle not found",
            },
            409: {
                "model": ErrorResponse,
                "description": "Spot already reserved or not available",
            },
            422: {"model": ErrorResponse, "description": "Validation error"},
        },
    )
    async def create_reservation(
        body: CreateReservationRequest,
    ) -> CreatedResponse:
        command: CreateReservation = CreateReservation(
            facility_id=body.facility_id,
            spot_id=body.spot_id,
            vehicle_id=body.vehicle_id,
            time_slot_start=body.time_slot_start,
            time_slot_end=body.time_slot_end,
            base_rate_amount=body.base_rate_amount,
            base_rate_currency=body.base_rate_currency,
        )
        reservation_id: str = await container.create_reservation_handler.handle(command)
        return CreatedResponse(id=reservation_id)

    @router.get(
        "/vehicle/{vehicle_id}",
        response_model=list[ReservationResponse],
        summary="List vehicle reservations",
        description="Retrieve all reservations associated with a specific vehicle.",
    )
    async def list_vehicle_reservations(
        vehicle_id: str,
    ) -> list[ReservationResponse]:
        query: ListVehicleReservations = ListVehicleReservations(
            vehicle_id=vehicle_id,
        )
        dtos = await container.list_vehicle_reservations_handler.handle(query)
        return [
            ReservationResponse(
                reservation_id=dto.reservation_id,
                facility_id=dto.facility_id,
                spot_id=dto.spot_id,
                vehicle_id=dto.vehicle_id,
                time_slot_start=dto.time_slot_start,
                time_slot_end=dto.time_slot_end,
                status=dto.status,
                total_cost_amount=dto.total_cost_amount,
                total_cost_currency=dto.total_cost_currency,
                created_at=dto.created_at,
            )
            for dto in dtos
        ]

    @router.get(
        "/{reservation_id}",
        response_model=ReservationResponse,
        summary="Get reservation details",
        description="Retrieve a reservation by its ID.",
        responses={
            404: {"model": ErrorResponse, "description": "Reservation not found"},
        },
    )
    async def get_reservation(reservation_id: str) -> ReservationResponse:
        query: GetReservationDetails = GetReservationDetails(
            reservation_id=reservation_id,
        )
        dto = await container.get_reservation_details_handler.handle(query)
        return ReservationResponse(
            reservation_id=dto.reservation_id,
            facility_id=dto.facility_id,
            spot_id=dto.spot_id,
            vehicle_id=dto.vehicle_id,
            time_slot_start=dto.time_slot_start,
            time_slot_end=dto.time_slot_end,
            status=dto.status,
            total_cost_amount=dto.total_cost_amount,
            total_cost_currency=dto.total_cost_currency,
            created_at=dto.created_at,
        )

    @router.put(
        "/{reservation_id}/confirm",
        status_code=204,
        summary="Confirm a reservation",
        description="Transition a pending reservation to confirmed status.",
        responses={
            404: {"model": ErrorResponse, "description": "Reservation not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
        },
    )
    async def confirm_reservation(reservation_id: str) -> Response:
        command: ConfirmReservation = ConfirmReservation(
            reservation_id=reservation_id,
        )
        await container.confirm_reservation_handler.handle(command)
        return Response(status_code=204)

    @router.put(
        "/{reservation_id}/activate",
        status_code=204,
        summary="Activate a reservation",
        description="Transition a confirmed reservation to active status when the vehicle arrives.",
        responses={
            404: {"model": ErrorResponse, "description": "Reservation not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
        },
    )
    async def activate_reservation(reservation_id: str) -> Response:
        command: ActivateReservation = ActivateReservation(
            reservation_id=reservation_id,
        )
        await container.activate_reservation_handler.handle(command)
        return Response(status_code=204)

    @router.put(
        "/{reservation_id}/complete",
        status_code=204,
        summary="Complete a reservation",
        description="Mark an active reservation as completed when the vehicle departs.",
        responses={
            404: {"model": ErrorResponse, "description": "Reservation not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
        },
    )
    async def complete_reservation(reservation_id: str) -> Response:
        command: CompleteReservation = CompleteReservation(
            reservation_id=reservation_id,
        )
        await container.complete_reservation_handler.handle(command)
        return Response(status_code=204)

    @router.put(
        "/{reservation_id}/cancel",
        status_code=204,
        summary="Cancel a reservation",
        description="Cancel a reservation with an optional reason. Releases the reserved spot.",
        responses={
            404: {"model": ErrorResponse, "description": "Reservation not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
        },
    )
    async def cancel_reservation(
        reservation_id: str, body: CancelReservationRequest
    ) -> Response:
        command: CancelReservation = CancelReservation(
            reservation_id=reservation_id,
            reason=body.reason,
        )
        await container.cancel_reservation_handler.handle(command)
        return Response(status_code=204)

    @router.put(
        "/{reservation_id}/extend",
        status_code=204,
        summary="Extend a reservation",
        description="Extend the end time of an existing reservation.",
        responses={
            404: {"model": ErrorResponse, "description": "Reservation not found"},
            409: {
                "model": ErrorResponse,
                "description": "Invalid state transition",
            },
            422: {"model": ErrorResponse, "description": "Validation error"},
        },
    )
    async def extend_reservation(
        reservation_id: str, body: ExtendReservationRequest
    ) -> Response:
        command: ExtendReservation = ExtendReservation(
            reservation_id=reservation_id,
            new_end=body.new_end,
        )
        await container.extend_reservation_handler.handle(command)
        return Response(status_code=204)

    return router

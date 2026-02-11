from dataclasses import dataclass
from datetime import datetime

from parkly.domain.model.reservation import Reservation


@dataclass(frozen=True)
class ReservationDTO:
    reservation_id: str
    facility_id: str
    spot_id: str
    vehicle_id: str
    time_slot_start: datetime
    time_slot_end: datetime
    status: str
    total_cost_amount: str
    total_cost_currency: str
    created_at: datetime

    @staticmethod
    def from_domain(reservation: Reservation) -> "ReservationDTO":
        return ReservationDTO(
            reservation_id=str(reservation.id.value),
            facility_id=str(reservation.facility_id.value),
            spot_id=str(reservation.spot_id.value),
            vehicle_id=str(reservation.vehicle_id.value),
            time_slot_start=reservation.time_slot.start,
            time_slot_end=reservation.time_slot.end,
            status=reservation.status.value,
            total_cost_amount=str(reservation.total_cost.amount),
            total_cost_currency=str(reservation.total_cost.currency),
            created_at=reservation.created_at,
        )

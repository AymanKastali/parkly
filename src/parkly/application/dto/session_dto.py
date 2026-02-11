from dataclasses import dataclass
from datetime import datetime

from parkly.domain.model.parking_session import ParkingSession


@dataclass(frozen=True)
class SessionDTO:
    session_id: str
    reservation_id: str | None
    facility_id: str
    spot_id: str
    vehicle_id: str
    entry_time: datetime
    exit_time: datetime | None
    total_cost_amount: str
    total_cost_currency: str
    is_active: bool

    @staticmethod
    def from_domain(session: ParkingSession) -> "SessionDTO":
        return SessionDTO(
            session_id=str(session.id.value),
            reservation_id=(
                str(session.reservation_id.value)
                if session.reservation_id is not None
                else None
            ),
            facility_id=str(session.facility_id.value),
            spot_id=str(session.spot_id.value),
            vehicle_id=str(session.vehicle_id.value),
            entry_time=session.entry_time,
            exit_time=session.exit_time,
            total_cost_amount=str(session.total_cost.amount),
            total_cost_currency=str(session.total_cost.currency),
            is_active=session.is_active,
        )

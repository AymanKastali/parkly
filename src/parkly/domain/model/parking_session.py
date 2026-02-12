from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Self

from parkly.domain.event.events import (
    SessionEnded,
    SessionExtended,
    SessionStarted,
)
from parkly.domain.exception.exceptions import (
    RequiredFieldError,
    SessionAlreadyEndedError,
)
from parkly.domain.model.typed_ids import (
    FacilityId,
    ReservationId,
    SessionId,
    SpotId,
    VehicleId,
)
from parkly.domain.model.consts import SECONDS_PER_HOUR
from parkly.domain.model.value_objects import Money
from parkly.domain.model.entity import AggregateRoot


@dataclass
class ParkingSession(AggregateRoot[SessionId]):
    _reservation_id: ReservationId | None
    _facility_id: FacilityId
    _spot_id: SpotId
    _vehicle_id: VehicleId
    _entry_time: datetime
    _exit_time: datetime | None
    _total_cost: Money

    @property
    def reservation_id(self) -> ReservationId | None:
        return self._reservation_id

    @property
    def facility_id(self) -> FacilityId:
        return self._facility_id

    @property
    def spot_id(self) -> SpotId:
        return self._spot_id

    @property
    def vehicle_id(self) -> VehicleId:
        return self._vehicle_id

    @property
    def entry_time(self) -> datetime:
        return self._entry_time

    @property
    def exit_time(self) -> datetime | None:
        return self._exit_time

    @property
    def total_cost(self) -> Money:
        return self._total_cost

    @property
    def is_active(self) -> bool:
        return self._exit_time is None

    @classmethod
    def create(
        cls,
        session_id: SessionId,
        facility_id: FacilityId,
        spot_id: SpotId,
        vehicle_id: VehicleId,
        entry_time: datetime,
        total_cost: Money,
        occurred_at: datetime,
        reservation_id: ReservationId | None = None,
        exit_time: datetime | None = None,
    ) -> Self:
        if session_id is None:
            raise RequiredFieldError(cls.__name__, "session_id")
        if facility_id is None:
            raise RequiredFieldError(cls.__name__, "facility_id")
        if spot_id is None:
            raise RequiredFieldError(cls.__name__, "spot_id")
        if vehicle_id is None:
            raise RequiredFieldError(cls.__name__, "vehicle_id")
        if entry_time is None:
            raise RequiredFieldError(cls.__name__, "entry_time")
        if total_cost is None:
            raise RequiredFieldError(cls.__name__, "total_cost")
        session = cls(
            _id=session_id,
            _reservation_id=reservation_id,
            _facility_id=facility_id,
            _spot_id=spot_id,
            _vehicle_id=vehicle_id,
            _entry_time=entry_time,
            _exit_time=exit_time,
            _total_cost=total_cost,
        )
        session._record_event(
            SessionStarted(
                session_id=session_id,
                facility_id=facility_id,
                spot_id=spot_id,
                vehicle_id=vehicle_id,
                occurred_at=occurred_at,
            )
        )
        return session

    @classmethod
    def reconstitute(
        cls,
        session_id: SessionId,
        facility_id: FacilityId,
        spot_id: SpotId,
        vehicle_id: VehicleId,
        entry_time: datetime,
        total_cost: Money,
        reservation_id: ReservationId | None = None,
        exit_time: datetime | None = None,
    ) -> Self:
        return cls(
            _id=session_id,
            _reservation_id=reservation_id,
            _facility_id=facility_id,
            _spot_id=spot_id,
            _vehicle_id=vehicle_id,
            _entry_time=entry_time,
            _exit_time=exit_time,
            _total_cost=total_cost,
        )

    def extend(
        self, new_end: datetime, new_total_cost: Money, occurred_at: datetime
    ) -> None:
        if not self.is_active:
            raise SessionAlreadyEndedError()
        self._total_cost = new_total_cost
        self._record_event(
            SessionExtended(
                session_id=self._id,
                new_end=new_end,
                new_total_cost=new_total_cost,
                occurred_at=occurred_at,
            )
        )

    def end(
        self, total_cost: Money, exit_time: datetime, occurred_at: datetime
    ) -> None:
        if not self.is_active:
            raise SessionAlreadyEndedError()
        self._exit_time = exit_time
        self._total_cost = total_cost
        self._record_event(
            SessionEnded(
                session_id=self._id,
                total_cost=total_cost,
                occurred_at=occurred_at,
            )
        )

    def calculate_cost(self, rate_per_hour: Money, current_time: datetime) -> Money:
        end = self._exit_time or current_time
        duration_seconds = (end - self._entry_time).total_seconds()
        hours = Decimal(str(duration_seconds)) / SECONDS_PER_HOUR
        return rate_per_hour.multiply(hours)

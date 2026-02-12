from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Self

from parkly.domain.event.events import (
    ReservationActivated,
    ReservationCancelled,
    ReservationCompleted,
    ReservationConfirmed,
    ReservationCreated,
)
from parkly.domain.exception.exceptions import (
    InvalidExtensionError,
    InvalidStatusTransitionError,
    RequiredFieldError,
    ReservationNotExtendableError,
)
from parkly.domain.model.enums import ReservationStatus
from parkly.domain.model.typed_ids import (
    FacilityId,
    ReservationId,
    SpotId,
    VehicleId,
)
from parkly.domain.model.value_objects import Money, TimeSlot
from parkly.domain.model.entity import AggregateRoot


@dataclass
class Reservation(AggregateRoot[ReservationId]):
    _VALID_TRANSITIONS: ClassVar[dict[ReservationStatus, set[ReservationStatus]]] = {
        ReservationStatus.PENDING: {
            ReservationStatus.CONFIRMED,
            ReservationStatus.CANCELLED,
        },
        ReservationStatus.CONFIRMED: {
            ReservationStatus.ACTIVE,
            ReservationStatus.CANCELLED,
        },
        ReservationStatus.ACTIVE: {
            ReservationStatus.COMPLETED,
            ReservationStatus.CANCELLED,
        },
        ReservationStatus.COMPLETED: set(),
        ReservationStatus.CANCELLED: set(),
    }

    _facility_id: FacilityId
    _spot_id: SpotId
    _vehicle_id: VehicleId
    _time_slot: TimeSlot
    _status: ReservationStatus
    _total_cost: Money
    _created_at: datetime

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
    def time_slot(self) -> TimeSlot:
        return self._time_slot

    @property
    def status(self) -> ReservationStatus:
        return self._status

    @property
    def total_cost(self) -> Money:
        return self._total_cost

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def _transition_to(self, new_status: ReservationStatus) -> None:
        allowed = self._VALID_TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                from_status=self._status.value, to_status=new_status.value
            )
        self._status = new_status

    @classmethod
    def create(
        cls,
        reservation_id: ReservationId,
        facility_id: FacilityId,
        spot_id: SpotId,
        vehicle_id: VehicleId,
        time_slot: TimeSlot,
        status: ReservationStatus,
        total_cost: Money,
        created_at: datetime,
        occurred_at: datetime,
    ) -> Self:
        if reservation_id is None:
            raise RequiredFieldError(cls.__name__, "reservation_id")
        if facility_id is None:
            raise RequiredFieldError(cls.__name__, "facility_id")
        if spot_id is None:
            raise RequiredFieldError(cls.__name__, "spot_id")
        if vehicle_id is None:
            raise RequiredFieldError(cls.__name__, "vehicle_id")
        if time_slot is None:
            raise RequiredFieldError(cls.__name__, "time_slot")
        if status is None:
            raise RequiredFieldError(cls.__name__, "status")
        if total_cost is None:
            raise RequiredFieldError(cls.__name__, "total_cost")
        if created_at is None:
            raise RequiredFieldError(cls.__name__, "created_at")
        if status != ReservationStatus.PENDING:
            raise InvalidStatusTransitionError(
                from_status="(initial)", to_status=status.value
            )
        reservation = cls(
            _id=reservation_id,
            _facility_id=facility_id,
            _spot_id=spot_id,
            _vehicle_id=vehicle_id,
            _time_slot=time_slot,
            _status=status,
            _total_cost=total_cost,
            _created_at=created_at,
        )
        reservation._record_event(
            ReservationCreated(
                reservation_id=reservation_id,
                facility_id=facility_id,
                spot_id=spot_id,
                vehicle_id=vehicle_id,
                time_slot=time_slot,
                occurred_at=occurred_at,
            )
        )
        return reservation

    @classmethod
    def reconstitute(
        cls,
        reservation_id: ReservationId,
        facility_id: FacilityId,
        spot_id: SpotId,
        vehicle_id: VehicleId,
        time_slot: TimeSlot,
        status: ReservationStatus,
        total_cost: Money,
        created_at: datetime,
    ) -> Self:
        return cls(
            _id=reservation_id,
            _facility_id=facility_id,
            _spot_id=spot_id,
            _vehicle_id=vehicle_id,
            _time_slot=time_slot,
            _status=status,
            _total_cost=total_cost,
            _created_at=created_at,
        )

    def confirm(self, occurred_at: datetime) -> None:
        self._transition_to(ReservationStatus.CONFIRMED)
        self._record_event(
            ReservationConfirmed(
                reservation_id=self._id,
                occurred_at=occurred_at,
            )
        )

    def activate(self, occurred_at: datetime) -> None:
        self._transition_to(ReservationStatus.ACTIVE)
        self._record_event(
            ReservationActivated(
                reservation_id=self._id,
                occurred_at=occurred_at,
            )
        )

    def complete(self, occurred_at: datetime) -> None:
        self._transition_to(ReservationStatus.COMPLETED)
        self._record_event(
            ReservationCompleted(
                reservation_id=self._id,
                occurred_at=occurred_at,
            )
        )

    def cancel(self, occurred_at: datetime, reason: str = "") -> None:
        self._transition_to(ReservationStatus.CANCELLED)
        self._record_event(
            ReservationCancelled(
                reservation_id=self._id,
                reason=reason,
                occurred_at=occurred_at,
            )
        )

    def extend(self, new_end: datetime) -> None:
        if self._status not in (
            ReservationStatus.CONFIRMED,
            ReservationStatus.ACTIVE,
        ):
            raise ReservationNotExtendableError(status=self._status.value)
        if new_end <= self._time_slot.end:
            raise InvalidExtensionError()
        self._time_slot = TimeSlot(start=self._time_slot.start, end=new_end)

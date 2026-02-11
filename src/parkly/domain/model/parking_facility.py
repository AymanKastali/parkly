from dataclasses import dataclass, field
from typing import Self

from parkly.domain.event.events import FacilityCreated, SpotAdded, SpotRemoved
from parkly.domain.exception.exceptions import (
    CapacityExceededError,
    DuplicateSpotError,
    RequiredFieldError,
    SpotNotAvailableError,
    SpotNotFoundError,
)
from parkly.domain.model.enums import (
    AccessControlMethod,
    FacilityType,
    SpotStatus,
    SpotType,
)
from parkly.domain.model.entity import AggregateRoot, Entity
from parkly.domain.model.typed_ids import FacilityId, SpotId
from parkly.domain.model.value_objects import (
    Capacity,
    FacilityName,
    Location,
    SpotNumber,
    TimeSlot,
)


@dataclass
class ParkingSpot(Entity[SpotId]):
    _spot_number: SpotNumber
    _spot_type: SpotType
    _status: SpotStatus

    @classmethod
    def create(
        cls,
        spot_id: SpotId,
        spot_number: SpotNumber,
        spot_type: SpotType,
        status: SpotStatus,
    ) -> Self:
        if spot_id is None:
            raise RequiredFieldError(cls.__name__, "spot_id")
        if spot_number is None:
            raise RequiredFieldError(cls.__name__, "spot_number")
        if spot_type is None:
            raise RequiredFieldError(cls.__name__, "spot_type")
        if status is None:
            raise RequiredFieldError(cls.__name__, "status")
        return cls(
            _id=spot_id,
            _spot_number=spot_number,
            _spot_type=spot_type,
            _status=status,
        )

    @classmethod
    def reconstitute(
        cls,
        spot_id: SpotId,
        spot_number: SpotNumber,
        spot_type: SpotType,
        status: SpotStatus,
    ) -> Self:
        return cls(
            _id=spot_id,
            _spot_number=spot_number,
            _spot_type=spot_type,
            _status=status,
        )

    @property
    def spot_number(self) -> SpotNumber:
        return self._spot_number

    @property
    def spot_type(self) -> SpotType:
        return self._spot_type

    @property
    def status(self) -> SpotStatus:
        return self._status

    def is_available(self, time_slot: TimeSlot) -> bool:
        return self._status == SpotStatus.AVAILABLE

    def reserve(self) -> None:
        if self._status != SpotStatus.AVAILABLE:
            raise SpotNotAvailableError(spot_identifier=str(self._spot_number))
        self._status = SpotStatus.RESERVED

    def release(self) -> None:
        self._status = SpotStatus.AVAILABLE


@dataclass
class ParkingFacility(AggregateRoot[FacilityId]):
    _name: FacilityName
    _location: Location
    _facility_type: FacilityType
    _access_control: AccessControlMethod
    _total_capacity: Capacity
    _spots: list[ParkingSpot] = field(default_factory=list)

    @property
    def name(self) -> FacilityName:
        return self._name

    @property
    def location(self) -> Location:
        return self._location

    @property
    def facility_type(self) -> FacilityType:
        return self._facility_type

    @property
    def access_control(self) -> AccessControlMethod:
        return self._access_control

    @property
    def total_capacity(self) -> Capacity:
        return self._total_capacity

    @property
    def spots(self) -> list[ParkingSpot]:
        return list(self._spots)

    @classmethod
    def create(
        cls,
        facility_id: FacilityId,
        name: FacilityName,
        location: Location,
        facility_type: FacilityType,
        access_control: AccessControlMethod,
        total_capacity: Capacity,
    ) -> Self:
        if facility_id is None:
            raise RequiredFieldError(cls.__name__, "facility_id")
        if name is None:
            raise RequiredFieldError(cls.__name__, "name")
        if location is None:
            raise RequiredFieldError(cls.__name__, "location")
        if facility_type is None:
            raise RequiredFieldError(cls.__name__, "facility_type")
        if access_control is None:
            raise RequiredFieldError(cls.__name__, "access_control")
        if total_capacity is None:
            raise RequiredFieldError(cls.__name__, "total_capacity")
        facility = cls(
            _id=facility_id,
            _name=name,
            _location=location,
            _facility_type=facility_type,
            _access_control=access_control,
            _total_capacity=total_capacity,
        )
        facility._record_event(
            FacilityCreated(
                facility_id=facility_id,
            )
        )
        return facility

    @classmethod
    def reconstitute(
        cls,
        facility_id: FacilityId,
        name: FacilityName,
        location: Location,
        facility_type: FacilityType,
        access_control: AccessControlMethod,
        total_capacity: Capacity,
        spots: list[ParkingSpot] | None = None,
    ) -> Self:
        return cls(
            _id=facility_id,
            _name=name,
            _location=location,
            _facility_type=facility_type,
            _access_control=access_control,
            _total_capacity=total_capacity,
            _spots=spots if spots is not None else [],
        )

    def add_spot(
        self,
        spot_id: SpotId,
        spot_number: SpotNumber,
        spot_type: SpotType,
        status: SpotStatus,
    ) -> None:
        if len(self._spots) >= self._total_capacity.value:
            raise CapacityExceededError(
                facility_name=str(self._name), capacity=self._total_capacity.value
            )
        for existing in self._spots:
            if existing.id == spot_id:
                raise DuplicateSpotError(spot_id=spot_id)
        spot = ParkingSpot.create(
            spot_id=spot_id,
            spot_number=spot_number,
            spot_type=spot_type,
            status=status,
        )
        self._spots.append(spot)
        self._record_event(
            SpotAdded(
                facility_id=self._id,
                spot_id=spot_id,
                spot_type=spot_type,
            )
        )

    def remove_spot(self, spot_id: SpotId) -> None:
        for i, spot in enumerate(self._spots):
            if spot.id == spot_id:
                self._spots.pop(i)
                self._record_event(
                    SpotRemoved(
                        facility_id=self._id,
                        spot_id=spot_id,
                    )
                )
                return
        raise SpotNotFoundError(spot_id=spot_id)

    def reserve_spot(self, spot_id: SpotId) -> None:
        for spot in self._spots:
            if spot.id == spot_id:
                spot.reserve()
                return
        raise SpotNotFoundError(spot_id=spot_id)

    def release_spot(self, spot_id: SpotId) -> None:
        for spot in self._spots:
            if spot.id == spot_id:
                spot.release()
                return
        raise SpotNotFoundError(spot_id=spot_id)

    def get_available_spots(
        self,
        time_slot: TimeSlot,
        spot_type: SpotType | None = None,
    ) -> list[ParkingSpot]:
        available: list[ParkingSpot] = []
        for spot in self._spots:
            if spot_type is not None and spot.spot_type != spot_type:
                continue
            if spot.is_available(time_slot):
                available.append(spot)
        return available

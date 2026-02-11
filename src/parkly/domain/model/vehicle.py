from dataclasses import dataclass
from typing import ClassVar, Self

from parkly.domain.event.events import VehicleRegistered
from parkly.domain.exception.exceptions import RequiredFieldError
from parkly.domain.model.enums import SpotType, VehicleType
from parkly.domain.model.typed_ids import OwnerId, VehicleId
from parkly.domain.model.value_objects import LicensePlate
from parkly.domain.model.entity import AggregateRoot


@dataclass
class Vehicle(AggregateRoot[VehicleId]):
    _SPOT_ELIGIBILITY: ClassVar[dict[VehicleType, list[SpotType]]] = {
        VehicleType.CAR: [
            SpotType.STANDARD,
            SpotType.HANDICAPPED,
        ],
        VehicleType.MOTORCYCLE: [
            SpotType.MOTORCYCLE,
        ],
        VehicleType.TRUCK: [
            SpotType.OVERSIZED,
        ],
        VehicleType.BICYCLE: [
            SpotType.BICYCLE,
        ],
    }

    _owner_id: OwnerId
    _license_plate: LicensePlate
    _vehicle_type: VehicleType
    _is_ev: bool

    @property
    def owner_id(self) -> OwnerId:
        return self._owner_id

    @property
    def license_plate(self) -> LicensePlate:
        return self._license_plate

    @property
    def vehicle_type(self) -> VehicleType:
        return self._vehicle_type

    @property
    def is_ev(self) -> bool:
        return self._is_ev

    @classmethod
    def create(
        cls,
        vehicle_id: VehicleId,
        owner_id: OwnerId,
        license_plate: LicensePlate,
        vehicle_type: VehicleType,
        is_ev: bool,
    ) -> Self:
        if vehicle_id is None:
            raise RequiredFieldError(cls.__name__, "vehicle_id")
        if owner_id is None:
            raise RequiredFieldError(cls.__name__, "owner_id")
        if license_plate is None:
            raise RequiredFieldError(cls.__name__, "license_plate")
        if vehicle_type is None:
            raise RequiredFieldError(cls.__name__, "vehicle_type")
        if is_ev is None:
            raise RequiredFieldError(cls.__name__, "is_ev")
        vehicle = cls(
            _id=vehicle_id,
            _owner_id=owner_id,
            _license_plate=license_plate,
            _vehicle_type=vehicle_type,
            _is_ev=is_ev,
        )
        vehicle._record_event(
            VehicleRegistered(
                vehicle_id=vehicle_id,
                owner_id=owner_id,
                license_plate=license_plate,
            )
        )
        return vehicle

    @classmethod
    def reconstitute(
        cls,
        vehicle_id: VehicleId,
        owner_id: OwnerId,
        license_plate: LicensePlate,
        vehicle_type: VehicleType,
        is_ev: bool,
    ) -> Self:
        return cls(
            _id=vehicle_id,
            _owner_id=owner_id,
            _license_plate=license_plate,
            _vehicle_type=vehicle_type,
            _is_ev=is_ev,
        )

    def eligible_spot_types(self) -> list[SpotType]:
        base = list(self._SPOT_ELIGIBILITY.get(self._vehicle_type, []))
        if self._is_ev and SpotType.EV_CHARGING not in base:
            base.append(SpotType.EV_CHARGING)
        return base

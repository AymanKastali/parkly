from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt
from typing import Self

from parkly.domain.exception.exceptions import (
    CurrencyMismatchError,
    EmptyLicensePlateRegionError,
    EmptyLicensePlateValueError,
    InvalidCurrencyCodeError,
    InvalidLatitudeError,
    InvalidLongitudeError,
    InvalidTimeSlotError,
    NegativeMoneyAmountError,
    NegativeMoneyResultError,
    NonDecimalMoneyAmountError,
    RequiredFieldError,
)
from parkly.domain.model.consts import EARTH_RADIUS_KM, ISO_4217_CODES


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start is None:
            raise RequiredFieldError(type(self).__name__, "start")
        if self.end is None:
            raise RequiredFieldError(type(self).__name__, "end")
        if self.start >= self.end:
            raise InvalidTimeSlotError()

    def overlaps(self, other: "TimeSlot") -> bool:
        return self.start < other.end and other.start < self.end

    def is_adjacent(self, other: "TimeSlot") -> bool:
        return self.end == other.start or other.end == self.start

    def duration(self) -> timedelta:
        return self.end - self.start


@dataclass(frozen=True)
class Currency:
    code: str

    def __post_init__(self) -> None:
        if not self.code or self.code.upper() not in ISO_4217_CODES:
            raise InvalidCurrencyCodeError(self.code if self.code else "")
        object.__setattr__(self, "code", self.code.upper())

    def __str__(self) -> str:
        return self.code


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise NonDecimalMoneyAmountError()
        if self.amount < Decimal("0"):
            raise NegativeMoneyAmountError()
        if self.currency is None:
            raise RequiredFieldError(type(self).__name__, "currency")

    def _check_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                currency_a=str(self.currency), currency_b=str(other.currency)
            )

    def add(self, other: "Money") -> Self:
        self._check_same_currency(other)
        return type(self)(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> Self:
        self._check_same_currency(other)
        result = self.amount - other.amount
        if result < Decimal("0"):
            raise NegativeMoneyResultError()
        return type(self)(amount=result, currency=self.currency)

    def multiply(self, factor: Decimal) -> Self:
        return type(self)(amount=self.amount * factor, currency=self.currency)


@dataclass(frozen=True)
class LicensePlate:
    value: str
    region: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyLicensePlateValueError()
        if not self.region or not self.region.strip():
            raise EmptyLicensePlateRegionError()

    def formatted(self) -> str:
        return f"[{self.region}] {self.value}"


@dataclass(frozen=True)
class Location:
    latitude: Decimal
    longitude: Decimal
    address: str

    def __post_init__(self) -> None:
        if self.latitude is None:
            raise RequiredFieldError(type(self).__name__, "latitude")
        if self.longitude is None:
            raise RequiredFieldError(type(self).__name__, "longitude")
        if not self.address or not self.address.strip():
            raise RequiredFieldError(type(self).__name__, "address")
        if not (Decimal("-90") <= self.latitude <= Decimal("90")):
            raise InvalidLatitudeError()
        if not (Decimal("-180") <= self.longitude <= Decimal("180")):
            raise InvalidLongitudeError()

    def distance_to(self, other: "Location") -> Decimal:
        lat1 = radians(float(self.latitude))
        lat2 = radians(float(other.latitude))
        dlat = radians(float(other.latitude - self.latitude))
        dlon = radians(float(other.longitude - self.longitude))
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return EARTH_RADIUS_KM * Decimal(str(c))

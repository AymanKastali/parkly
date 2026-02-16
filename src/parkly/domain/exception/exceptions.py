class DomainException(Exception):
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


# --- Validation errors (value object / construction validation) ---


class DomainValidationError(DomainException):
    code: str = "VALIDATION_ERROR"


class InvalidTimeSlotError(DomainValidationError):
    code: str = "INVALID_TIME_SLOT"

    def __init__(self) -> None:
        super().__init__("TimeSlot start must be before end")


class InvalidMoneyAmountError(DomainValidationError):
    """Base for money amount validation errors."""

    code: str = "INVALID_MONEY_AMOUNT"


class NonDecimalMoneyAmountError(InvalidMoneyAmountError):
    code: str = "NON_DECIMAL_MONEY_AMOUNT"

    def __init__(self) -> None:
        super().__init__("Money amount must be a Decimal")


class NegativeMoneyAmountError(InvalidMoneyAmountError):
    code: str = "NEGATIVE_MONEY_AMOUNT"

    def __init__(self) -> None:
        super().__init__("Money amount must be non-negative")


class InvalidCurrencyCodeError(DomainValidationError):
    code: str = "INVALID_CURRENCY_CODE"

    def __init__(self, code: str) -> None:
        self.currency_code = code
        super().__init__(f"Invalid ISO 4217 currency code: '{code}'")


class CurrencyMismatchError(DomainValidationError):
    code: str = "CURRENCY_MISMATCH"

    def __init__(self, currency_a: str, currency_b: str) -> None:
        self.currency_a = currency_a
        self.currency_b = currency_b
        super().__init__(
            f"Cannot operate on different currencies: {currency_a} vs {currency_b}"
        )


class NegativeMoneyResultError(DomainValidationError):
    code: str = "NEGATIVE_MONEY_RESULT"

    def __init__(self) -> None:
        super().__init__("Subtraction would result in negative amount")


class EmptyLicensePlateError(DomainValidationError):
    """Base for license plate emptiness errors."""

    code: str = "EMPTY_LICENSE_PLATE"


class EmptyLicensePlateValueError(EmptyLicensePlateError):
    code: str = "EMPTY_LICENSE_PLATE_VALUE"

    def __init__(self) -> None:
        super().__init__("License plate value must not be empty")


class EmptyLicensePlateRegionError(EmptyLicensePlateError):
    code: str = "EMPTY_LICENSE_PLATE_REGION"

    def __init__(self) -> None:
        super().__init__("License plate region must not be empty")


class EmptySpotNumberError(DomainValidationError):
    code: str = "EMPTY_SPOT_NUMBER"

    def __init__(self) -> None:
        super().__init__("Spot number must not be empty")


class InvalidLatitudeError(DomainValidationError):
    code: str = "INVALID_LATITUDE"

    def __init__(self) -> None:
        super().__init__("Latitude must be between -90 and 90")


class InvalidLongitudeError(DomainValidationError):
    code: str = "INVALID_LONGITUDE"

    def __init__(self) -> None:
        super().__init__("Longitude must be between -180 and 180")


class RequiredFieldError(DomainValidationError):
    code: str = "REQUIRED_FIELD"

    def __init__(self, entity_name: str, field_name: str) -> None:
        self.entity_name = entity_name
        self.field_name = field_name
        super().__init__(f"'{entity_name}.{field_name}' is required")


class NegativeCapacityError(DomainValidationError):
    code: str = "NEGATIVE_CAPACITY"

    def __init__(self) -> None:
        super().__init__("Total capacity must be non-negative")


class DuplicateSpotError(DomainValidationError):
    code: str = "DUPLICATE_SPOT"

    def __init__(self, spot_id: object) -> None:
        self.spot_id = spot_id
        super().__init__(f"Spot {spot_id} already exists in this facility")


class SpotNotFoundError(DomainValidationError):
    code: str = "SPOT_NOT_FOUND"

    def __init__(self, spot_id: object) -> None:
        self.spot_id = spot_id
        super().__init__(f"Spot {spot_id} not found in this facility")


class InvalidExtensionError(DomainValidationError):
    code: str = "INVALID_EXTENSION"

    def __init__(self) -> None:
        super().__init__("New end time must be after current end time")


class IneligibleSpotTypeError(DomainValidationError):
    code: str = "INELIGIBLE_SPOT_TYPE"

    def __init__(self, vehicle_type: str, spot_type: str) -> None:
        self.vehicle_type = vehicle_type
        self.spot_type = spot_type
        super().__init__(
            f"Vehicle type {vehicle_type} is not eligible for spot type {spot_type}"
        )


# --- Operation errors (lifecycle / state-machine violations) ---


class InvalidOperationError(DomainException):
    code: str = "INVALID_OPERATION"


class InvalidStatusTransitionError(InvalidOperationError):
    code: str = "INVALID_STATUS_TRANSITION"

    def __init__(self, from_status: str, to_status: str) -> None:
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Cannot transition from {from_status} to {to_status}")


class ReservationNotExtendableError(InvalidOperationError):
    code: str = "RESERVATION_NOT_EXTENDABLE"

    def __init__(self, status: str) -> None:
        self.status = status
        super().__init__(f"Cannot extend reservation in {status} status")


class SessionAlreadyEndedError(InvalidOperationError):
    code: str = "SESSION_ALREADY_ENDED"

    def __init__(self) -> None:
        super().__init__("Session has already ended")


class SpotAlreadyReservedError(InvalidOperationError):
    code: str = "SPOT_ALREADY_RESERVED"

    def __init__(self, spot_identifier: str) -> None:
        self.spot_identifier = spot_identifier
        super().__init__(f"Spot {spot_identifier} is already reserved")


# --- Specific domain errors ---


class SpotNotAvailableError(DomainException):
    code: str = "SPOT_NOT_AVAILABLE"

    def __init__(self, spot_identifier: str) -> None:
        self.spot_identifier = spot_identifier
        super().__init__(f"Spot {spot_identifier} is not available")


class CapacityExceededError(DomainException):
    code: str = "CAPACITY_EXCEEDED"

    def __init__(self, facility_name: str, capacity: int) -> None:
        self.facility_name = facility_name
        self.capacity = capacity
        super().__init__(
            f"Facility {facility_name} has reached its capacity of {capacity}"
        )


class DuplicateFacilityError(DomainException):
    code: str = "DUPLICATE_FACILITY"

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"A facility named '{name}' already exists at this location")


# --- Pricing config validation errors ---


class InvalidPeakHourRangeError(DomainValidationError):
    code: str = "INVALID_PEAK_HOUR_RANGE"

    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end
        super().__init__(
            f"Peak start hour ({start}) must be less than peak end hour ({end})"
        )


class InvalidHourValueError(DomainValidationError):
    code: str = "INVALID_HOUR_VALUE"

    def __init__(self, field_name: str, value: int) -> None:
        self.field_name = field_name
        self.value = value
        super().__init__(f"{field_name} must be between 0 and 23, got {value}")


class InvalidMultiplierError(DomainValidationError):
    code: str = "INVALID_MULTIPLIER"

    def __init__(self, field_name: str, value: object) -> None:
        self.field_name = field_name
        self.value = value
        super().__init__(f"{field_name} must be positive, got {value}")


class InvalidFreeHoursError(DomainValidationError):
    code: str = "INVALID_FREE_HOURS"

    def __init__(self, value: int) -> None:
        self.value = value
        super().__init__(f"free_hours must be non-negative, got {value}")

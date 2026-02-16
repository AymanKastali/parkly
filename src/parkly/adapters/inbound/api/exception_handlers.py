from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from parkly.adapters.inbound.api.auth_exceptions import (
    AuthenticationError,
    InsufficientRoleError,
)
from parkly.application.exception.exceptions import (
    ApplicationError,
    NotFoundError,
    SpotAlreadyOccupiedError,
)
from parkly.application.port.logger import Logger
from parkly.domain.exception.exceptions import (
    CapacityExceededError,
    DomainException,
    DomainValidationError,
    InvalidOperationError,
    SpotNotAvailableError,
)


def _error_response(status_code: int, exc: Exception, logger: Logger) -> JSONResponse:
    logger.warning(
        f"{type(exc).__name__}: {exc}",
        extra={"status_code": status_code, "error": type(exc).__name__},
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(exc).__name__,
            "detail": str(exc),
        },
    )


def register_exception_handlers(app: FastAPI, logger: Logger) -> None:
    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        return _error_response(401, exc, logger)

    @app.exception_handler(InsufficientRoleError)
    async def insufficient_role_handler(
        request: Request, exc: InsufficientRoleError
    ) -> JSONResponse:
        return _error_response(403, exc, logger)

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return _error_response(404, exc, logger)

    @app.exception_handler(DomainValidationError)
    async def validation_handler(
        request: Request, exc: DomainValidationError
    ) -> JSONResponse:
        return _error_response(422, exc, logger)

    @app.exception_handler(InvalidOperationError)
    async def invalid_operation_handler(
        request: Request, exc: InvalidOperationError
    ) -> JSONResponse:
        return _error_response(409, exc, logger)

    @app.exception_handler(SpotNotAvailableError)
    async def spot_not_available_handler(
        request: Request, exc: SpotNotAvailableError
    ) -> JSONResponse:
        return _error_response(409, exc, logger)

    @app.exception_handler(CapacityExceededError)
    async def capacity_exceeded_handler(
        request: Request, exc: CapacityExceededError
    ) -> JSONResponse:
        return _error_response(409, exc, logger)

    @app.exception_handler(SpotAlreadyOccupiedError)
    async def spot_already_occupied_handler(
        request: Request, exc: SpotAlreadyOccupiedError
    ) -> JSONResponse:
        return _error_response(409, exc, logger)

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return _error_response(422, exc, logger)

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return _error_response(400, exc, logger)

    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        return _error_response(400, exc, logger)

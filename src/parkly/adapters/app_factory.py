from fastapi import FastAPI

from parkly.adapters.config import AppSettings
from parkly.adapters.container import Container
from parkly.adapters.inbound.api.exception_handlers import register_exception_handlers
from parkly.adapters.inbound.api.facilities_router import create_facilities_router
from parkly.adapters.inbound.api.middleware import RequestLoggingMiddleware
from parkly.adapters.inbound.api.reservations_router import create_reservations_router
from parkly.adapters.inbound.api.sessions_router import create_sessions_router
from parkly.adapters.inbound.api.vehicles_router import create_vehicles_router

TAGS_METADATA: list[dict[str, str]] = [
    {
        "name": "Facilities",
        "description": "Manage parking facilities and their spots. Create facilities, add or remove spots, query availability by location or time slot.",
    },
    {
        "name": "Reservations",
        "description": "Reservation lifecycle management. Create, confirm, activate, complete, cancel, or extend reservations.",
    },
    {
        "name": "Sessions",
        "description": "Parking session management. Start a session on entry, extend mid-session, and end on exit with cost calculation.",
    },
    {
        "name": "Vehicles",
        "description": "Vehicle registration. Register vehicles with license plate, type, and EV status. List vehicles by owner.",
    },
]


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings: AppSettings = settings or AppSettings()
    container: Container = Container(resolved_settings)

    app: FastAPI = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        description="Parking management platform supporting all vehicle types, reservations, dynamic pricing, real-time availability, and multi-method access control.",
        openapi_tags=TAGS_METADATA,
    )

    app.add_middleware(RequestLoggingMiddleware, logger=container.logger)
    register_exception_handlers(app, container.logger)

    app.include_router(create_facilities_router(container), prefix="/api/v1")
    app.include_router(create_reservations_router(container), prefix="/api/v1")
    app.include_router(create_sessions_router(container), prefix="/api/v1")
    app.include_router(create_vehicles_router(container), prefix="/api/v1")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await container.http_client.aclose()

    container.logger.info(
        "Application started",
        extra={
            "app_name": resolved_settings.app_name,
            "app_version": resolved_settings.app_version,
            "host": resolved_settings.host,
            "port": resolved_settings.port,
        },
    )

    return app

import httpx
from loggerizer import LogLevel

from parkly.adapters.config import AppSettings
from parkly.adapters.inbound.api.auth_dependency import AuthDependency, RequireRoles
from parkly.adapters.outbound.auth.goauth_client import GoAuthTokenValidator
from parkly.adapters.outbound.infrastructure.system_clock import SystemClock
from parkly.adapters.outbound.infrastructure.ulid_id_generator import (
    FacilityIdGenerator,
    ReservationIdGenerator,
    SessionIdGenerator,
    SpotIdGenerator,
    VehicleIdGenerator,
)
from parkly.adapters.outbound.logging.json_console_logger import JsonConsoleLogger
from parkly.adapters.outbound.messaging.in_memory_event_publisher import (
    InMemoryEventPublisher,
)
from parkly.adapters.outbound.persistence.database import (
    create_engine,
    create_session_factory,
)
from parkly.adapters.outbound.persistence.pg_parking_facility_repository import (
    PgParkingFacilityRepository,
)
from parkly.adapters.outbound.persistence.pg_parking_session_repository import (
    PgParkingSessionRepository,
)
from parkly.adapters.outbound.persistence.pg_reservation_repository import (
    PgReservationRepository,
)
from parkly.adapters.outbound.persistence.pg_vehicle_repository import (
    PgVehicleRepository,
)
from parkly.application.command.activate_reservation import ActivateReservationHandler
from parkly.application.command.add_parking_spot import AddParkingSpotHandler
from parkly.application.command.cancel_reservation import CancelReservationHandler
from parkly.application.command.complete_reservation import CompleteReservationHandler
from parkly.application.command.confirm_reservation import ConfirmReservationHandler
from parkly.application.command.create_parking_facility import (
    CreateParkingFacilityHandler,
)
from parkly.application.command.create_reservation import CreateReservationHandler
from parkly.application.command.end_parking_session import EndParkingSessionHandler
from parkly.application.command.extend_parking_session import (
    ExtendParkingSessionHandler,
)
from parkly.application.command.extend_reservation import ExtendReservationHandler
from parkly.application.command.register_vehicle import RegisterVehicleHandler
from parkly.application.command.remove_parking_spot import RemoveParkingSpotHandler
from parkly.application.command.start_parking_session import (
    StartParkingSessionHandler,
)
from parkly.application.event_handler.on_reservation_cancelled import (
    OnReservationCancelledReleaseSpot,
)
from parkly.application.event_handler.on_session_ended import (
    OnSessionEndedReleaseSpot,
)
from parkly.application.query.find_available_spots import FindAvailableSpotsHandler
from parkly.application.query.find_facilities_by_location import (
    FindFacilitiesByLocationHandler,
)
from parkly.application.query.get_facility_details import GetFacilityDetailsHandler
from parkly.application.query.get_reservation_details import (
    GetReservationDetailsHandler,
)
from parkly.application.query.get_session_details import GetSessionDetailsHandler
from parkly.application.query.list_owner_vehicles import ListOwnerVehiclesHandler
from parkly.application.query.list_vehicle_reservations import (
    ListVehicleReservationsHandler,
)
from parkly.application.query.list_vehicle_sessions import ListVehicleSessionsHandler
from parkly.domain.event.events import ReservationCancelled, SessionEnded
from parkly.application.port.token_validator import TokenValidator
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository
from parkly.domain.port.parking_session_repository import ParkingSessionRepository
from parkly.domain.port.reservation_repository import ReservationRepository
from parkly.domain.port.vehicle_repository import VehicleRepository
from parkly.domain.service.pricing_service import PricingService
from parkly.domain.service.pricing_strategy import StaticPricing


class Container:
    def __init__(self, settings: AppSettings) -> None:
        self.settings: AppSettings = settings

        # Infrastructure
        self.logger: JsonConsoleLogger = JsonConsoleLogger(
            level=LogLevel[settings.log_level.upper()],
        )
        self.clock: SystemClock = SystemClock()

        # Database
        self.engine = create_engine(
            database_url=settings.database_url,
            echo=settings.db_echo,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
        )
        self.session_factory = create_session_factory(self.engine)

        # Auth
        self.http_client: httpx.AsyncClient = httpx.AsyncClient()
        self.token_validator: TokenValidator = GoAuthTokenValidator(
            base_url=settings.auth_service_url,
            http_client=self.http_client,
        )
        self.auth_dependency: AuthDependency = AuthDependency(
            token_validator=self.token_validator,
        )
        self.admin_guard: RequireRoles = RequireRoles(
            auth=self.auth_dependency,
            roles={"admin", "super_admin"},
        )

        # ID generators
        self.facility_id_generator: FacilityIdGenerator = FacilityIdGenerator()
        self.spot_id_generator: SpotIdGenerator = SpotIdGenerator()
        self.reservation_id_generator: ReservationIdGenerator = ReservationIdGenerator()
        self.vehicle_id_generator: VehicleIdGenerator = VehicleIdGenerator()
        self.session_id_generator: SessionIdGenerator = SessionIdGenerator()

        # Repositories
        self.facility_repo: ParkingFacilityRepository = PgParkingFacilityRepository(
            session_factory=self.session_factory, logger=self.logger
        )
        self.reservation_repo: ReservationRepository = PgReservationRepository(
            session_factory=self.session_factory, logger=self.logger
        )
        self.session_repo: ParkingSessionRepository = PgParkingSessionRepository(
            session_factory=self.session_factory, logger=self.logger
        )
        self.vehicle_repo: VehicleRepository = PgVehicleRepository(
            session_factory=self.session_factory, logger=self.logger
        )

        # Domain services
        self.pricing_service: PricingService = PricingService(strategy=StaticPricing())

        # Event publisher
        self.event_publisher: InMemoryEventPublisher = InMemoryEventPublisher(
            logger=self.logger
        )

        # Command handlers
        self.create_parking_facility_handler: CreateParkingFacilityHandler = (
            CreateParkingFacilityHandler(
                facility_repo=self.facility_repo,
                id_generator=self.facility_id_generator,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.add_parking_spot_handler: AddParkingSpotHandler = AddParkingSpotHandler(
            facility_repo=self.facility_repo,
            id_generator=self.spot_id_generator,
            clock=self.clock,
            event_publisher=self.event_publisher,
            logger=self.logger,
        )
        self.remove_parking_spot_handler: RemoveParkingSpotHandler = (
            RemoveParkingSpotHandler(
                facility_repo=self.facility_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.register_vehicle_handler: RegisterVehicleHandler = RegisterVehicleHandler(
            vehicle_repo=self.vehicle_repo,
            id_generator=self.vehicle_id_generator,
            clock=self.clock,
            event_publisher=self.event_publisher,
            logger=self.logger,
        )
        self.create_reservation_handler: CreateReservationHandler = (
            CreateReservationHandler(
                facility_repo=self.facility_repo,
                reservation_repo=self.reservation_repo,
                vehicle_repo=self.vehicle_repo,
                id_generator=self.reservation_id_generator,
                pricing_service=self.pricing_service,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.confirm_reservation_handler: ConfirmReservationHandler = (
            ConfirmReservationHandler(
                reservation_repo=self.reservation_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.activate_reservation_handler: ActivateReservationHandler = (
            ActivateReservationHandler(
                reservation_repo=self.reservation_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.complete_reservation_handler: CompleteReservationHandler = (
            CompleteReservationHandler(
                reservation_repo=self.reservation_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.cancel_reservation_handler: CancelReservationHandler = (
            CancelReservationHandler(
                reservation_repo=self.reservation_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.extend_reservation_handler: ExtendReservationHandler = (
            ExtendReservationHandler(
                reservation_repo=self.reservation_repo,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.start_parking_session_handler: StartParkingSessionHandler = (
            StartParkingSessionHandler(
                session_repo=self.session_repo,
                facility_repo=self.facility_repo,
                id_generator=self.session_id_generator,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.extend_parking_session_handler: ExtendParkingSessionHandler = (
            ExtendParkingSessionHandler(
                session_repo=self.session_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        self.end_parking_session_handler: EndParkingSessionHandler = (
            EndParkingSessionHandler(
                session_repo=self.session_repo,
                clock=self.clock,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )

        # Query handlers
        self.find_available_spots_handler: FindAvailableSpotsHandler = (
            FindAvailableSpotsHandler(
                facility_repo=self.facility_repo,
                logger=self.logger,
            )
        )
        self.get_facility_details_handler: GetFacilityDetailsHandler = (
            GetFacilityDetailsHandler(
                facility_repo=self.facility_repo,
                logger=self.logger,
            )
        )
        self.get_reservation_details_handler: GetReservationDetailsHandler = (
            GetReservationDetailsHandler(
                reservation_repo=self.reservation_repo,
                logger=self.logger,
            )
        )
        self.get_session_details_handler: GetSessionDetailsHandler = (
            GetSessionDetailsHandler(
                session_repo=self.session_repo,
                logger=self.logger,
            )
        )
        self.list_owner_vehicles_handler: ListOwnerVehiclesHandler = (
            ListOwnerVehiclesHandler(
                vehicle_repo=self.vehicle_repo,
                logger=self.logger,
            )
        )
        self.list_vehicle_reservations_handler: ListVehicleReservationsHandler = (
            ListVehicleReservationsHandler(
                reservation_repo=self.reservation_repo,
                logger=self.logger,
            )
        )
        self.list_vehicle_sessions_handler: ListVehicleSessionsHandler = (
            ListVehicleSessionsHandler(
                session_repo=self.session_repo,
                logger=self.logger,
            )
        )
        self.find_facilities_by_location_handler: FindFacilitiesByLocationHandler = (
            FindFacilitiesByLocationHandler(
                facility_repo=self.facility_repo,
                logger=self.logger,
            )
        )

        # Event handlers
        on_reservation_cancelled: OnReservationCancelledReleaseSpot = (
            OnReservationCancelledReleaseSpot(
                reservation_repo=self.reservation_repo,
                facility_repo=self.facility_repo,
                event_publisher=self.event_publisher,
                logger=self.logger,
            )
        )
        on_session_ended: OnSessionEndedReleaseSpot = OnSessionEndedReleaseSpot(
            session_repo=self.session_repo,
            facility_repo=self.facility_repo,
            reservation_repo=self.reservation_repo,
            clock=self.clock,
            event_publisher=self.event_publisher,
            logger=self.logger,
        )
        self.event_publisher.register_handler(
            ReservationCancelled, on_reservation_cancelled
        )
        self.event_publisher.register_handler(SessionEnded, on_session_ended)

        self.logger.info(
            "Container initialized",
            extra={"log_level": settings.log_level},
        )

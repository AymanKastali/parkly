from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.event.events import SessionEnded
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository
from parkly.domain.port.parking_session_repository import ParkingSessionRepository
from parkly.domain.port.reservation_repository import ReservationRepository


class OnSessionEndedReleaseSpot:
    def __init__(
        self,
        session_repo: ParkingSessionRepository,
        facility_repo: ParkingFacilityRepository,
        reservation_repo: ReservationRepository,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._session_repo = session_repo
        self._facility_repo = facility_repo
        self._reservation_repo = reservation_repo
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, event: SessionEnded) -> None:
        self._logger.info(
            "Handling SessionEnded",
            extra={"session_id": str(event.session_id.value)},
        )

        session = await self._session_repo.find_by_id(event.session_id)
        if session is None:
            self._logger.warning(
                "Session not found, skipping spot release",
                extra={"session_id": str(event.session_id.value)},
            )
            return

        facility = await self._facility_repo.find_by_id(session.facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found, skipping spot release",
                extra={
                    "session_id": str(event.session_id.value),
                    "facility_id": str(session.facility_id.value),
                },
            )
            return

        facility.release_spot(session.spot_id)
        await self._facility_repo.save(facility)
        await self._event_publisher.publish(facility.collect_events())

        if session.reservation_id is not None:
            reservation = await self._reservation_repo.find_by_id(
                session.reservation_id
            )
            if reservation is not None:
                reservation.complete()
                await self._reservation_repo.save(reservation)
                await self._event_publisher.publish(reservation.collect_events())

        self._logger.info(
            "Spot released after session ended",
            extra={
                "session_id": str(event.session_id.value),
                "facility_id": str(session.facility_id.value),
                "spot_id": str(session.spot_id.value),
            },
        )

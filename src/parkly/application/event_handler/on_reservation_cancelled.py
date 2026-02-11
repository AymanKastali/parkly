from parkly.application.port.event_publisher import EventPublisher
from parkly.application.port.logger import Logger
from parkly.domain.event.events import ReservationCancelled
from parkly.domain.port.parking_facility_repository import ParkingFacilityRepository
from parkly.domain.port.reservation_repository import ReservationRepository


class OnReservationCancelledReleaseSpot:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        facility_repo: ParkingFacilityRepository,
        event_publisher: EventPublisher,
        logger: Logger,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._facility_repo = facility_repo
        self._event_publisher = event_publisher
        self._logger = logger

    async def handle(self, event: ReservationCancelled) -> None:
        self._logger.info(
            "Handling ReservationCancelled",
            extra={"reservation_id": str(event.reservation_id.value)},
        )

        reservation = await self._reservation_repo.find_by_id(event.reservation_id)
        if reservation is None:
            self._logger.warning(
                "Reservation not found, skipping spot release",
                extra={"reservation_id": str(event.reservation_id.value)},
            )
            return

        facility = await self._facility_repo.find_by_id(reservation.facility_id)
        if facility is None:
            self._logger.warning(
                "Facility not found, skipping spot release",
                extra={
                    "reservation_id": str(event.reservation_id.value),
                    "facility_id": str(reservation.facility_id.value),
                },
            )
            return

        facility.release_spot(reservation.spot_id)

        await self._facility_repo.save(facility)
        await self._event_publisher.publish(facility.collect_events())

        self._logger.info(
            "Spot released after reservation cancellation",
            extra={
                "reservation_id": str(event.reservation_id.value),
                "facility_id": str(reservation.facility_id.value),
                "spot_id": str(reservation.spot_id.value),
            },
        )

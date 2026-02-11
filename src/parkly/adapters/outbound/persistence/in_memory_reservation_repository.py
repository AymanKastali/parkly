from parkly.application.port.logger import Logger
from parkly.domain.model.reservation import Reservation
from parkly.domain.model.typed_ids import ReservationId, SpotId, VehicleId
from parkly.domain.model.value_objects import TimeSlot
from parkly.domain.port.reservation_repository import ReservationRepository


class InMemoryReservationRepository(ReservationRepository):
    def __init__(self, logger: Logger) -> None:
        self._store: dict[ReservationId, Reservation] = {}
        self._logger: Logger = logger

    async def save(self, reservation: Reservation) -> None:
        self._store[reservation.id] = reservation
        self._logger.debug(
            "Reservation saved",
            extra={"reservation_id": str(reservation.id.value)},
        )

    async def find_by_id(self, id: ReservationId) -> Reservation | None:
        result: Reservation | None = self._store.get(id)
        self._logger.debug(
            "Reservation lookup",
            extra={"reservation_id": str(id.value), "found": result is not None},
        )
        return result

    async def find_by_spot_and_time(
        self, spot_id: SpotId, time_slot: TimeSlot
    ) -> list[Reservation]:
        results: list[Reservation] = [
            reservation
            for reservation in self._store.values()
            if reservation.spot_id == spot_id
            and reservation.time_slot.overlaps(time_slot)
        ]
        self._logger.debug(
            "Reservation spot+time search",
            extra={"spot_id": str(spot_id.value), "found": len(results)},
        )
        return results

    async def find_by_vehicle(self, vehicle_id: VehicleId) -> list[Reservation]:
        results: list[Reservation] = [
            reservation
            for reservation in self._store.values()
            if reservation.vehicle_id == vehicle_id
        ]
        self._logger.debug(
            "Reservation vehicle search",
            extra={"vehicle_id": str(vehicle_id.value), "found": len(results)},
        )
        return results

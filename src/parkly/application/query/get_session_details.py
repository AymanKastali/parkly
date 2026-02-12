from dataclasses import dataclass

from parkly.application.dto.session_dto import SessionDTO
from parkly.application.exception.exceptions import SessionNotFoundError
from parkly.application.port.logger import Logger
from parkly.domain.model.identifiers import SessionId
from parkly.domain.port.parking_session_repository import ParkingSessionRepository


@dataclass(frozen=True)
class GetSessionDetails:
    session_id: str


class GetSessionDetailsHandler:
    def __init__(
        self,
        session_repo: ParkingSessionRepository,
        logger: Logger,
    ) -> None:
        self._session_repo = session_repo
        self._logger = logger

    async def handle(self, query: GetSessionDetails) -> SessionDTO:
        self._logger.debug(
            "Handling GetSessionDetails",
            extra={"session_id": str(query.session_id)},
        )

        session_id = SessionId(value=query.session_id)
        session = await self._session_repo.find_by_id(session_id)
        if session is None:
            self._logger.warning(
                "Session not found",
                extra={"session_id": str(query.session_id)},
            )
            raise SessionNotFoundError(session_id)

        self._logger.debug(
            "GetSessionDetails completed",
            extra={"session_id": str(query.session_id)},
        )
        return SessionDTO.from_domain(session)

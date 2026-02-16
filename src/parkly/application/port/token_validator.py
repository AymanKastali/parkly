from abc import ABC, abstractmethod

from parkly.application.dto.authenticated_user import AuthenticatedUser


class TokenValidator(ABC):
    @abstractmethod
    async def validate(self, token: str) -> AuthenticatedUser: ...

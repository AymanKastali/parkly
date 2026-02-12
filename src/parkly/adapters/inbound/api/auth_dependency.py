from fastapi import Request

from parkly.adapters.inbound.api.auth_exceptions import (
    InsufficientRoleError,
    MissingTokenError,
)
from parkly.application.dto.authenticated_user import AuthenticatedUser
from parkly.application.port.token_validator import TokenValidator


class AuthDependency:
    def __init__(self, token_validator: TokenValidator) -> None:
        self._token_validator = token_validator

    async def __call__(self, request: Request) -> AuthenticatedUser:
        authorization = request.headers.get("Authorization")
        if authorization is None or not authorization.startswith("Bearer "):
            raise MissingTokenError()
        token = authorization[7:]
        return await self._token_validator.validate(token)


class RequireRoles:
    def __init__(self, auth: AuthDependency, roles: set[str]) -> None:
        self._auth = auth
        self._roles = roles

    async def __call__(self, request: Request) -> AuthenticatedUser:
        user = await self._auth(request)
        if not self._roles & set(user.roles):
            raise InsufficientRoleError(required=self._roles, actual=user.roles)
        return user

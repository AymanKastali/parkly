from unittest.mock import AsyncMock

import pytest
from starlette.requests import Request

from parkly.adapters.inbound.api.auth_dependency import AuthDependency, RequireRoles
from parkly.adapters.inbound.api.auth_exceptions import (
    InsufficientRoleError,
    MissingTokenError,
)
from parkly.application.dto.authenticated_user import AuthenticatedUser
from parkly.application.port.token_validator import TokenValidator


def _make_request(headers: dict[str, str] | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/facilities",
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in (headers or {}).items()
        ],
    }
    return Request(scope)


@pytest.fixture
def token_validator() -> AsyncMock:
    return AsyncMock(spec=TokenValidator)


@pytest.fixture
def auth_dependency(token_validator: AsyncMock) -> AuthDependency:
    return AuthDependency(token_validator=token_validator)


class TestAuthDependency:
    async def test_raises_missing_token_when_no_authorization_header(
        self, auth_dependency: AuthDependency
    ) -> None:
        request = _make_request()
        with pytest.raises(MissingTokenError):
            await auth_dependency(request)

    async def test_raises_missing_token_when_not_bearer(
        self, auth_dependency: AuthDependency
    ) -> None:
        request = _make_request({"Authorization": "Basic abc123"})
        with pytest.raises(MissingTokenError):
            await auth_dependency(request)

    async def test_returns_authenticated_user_on_valid_token(
        self,
        auth_dependency: AuthDependency,
        token_validator: AsyncMock,
    ) -> None:
        expected_user = AuthenticatedUser(
            user_id="user-1",
            session_id="sess-1",
            roles=("admin",),
            permissions=("facility:read",),
        )
        token_validator.validate.return_value = expected_user

        request = _make_request({"Authorization": "Bearer valid-token"})
        result = await auth_dependency(request)

        assert result == expected_user
        token_validator.validate.assert_called_once_with("valid-token")


class TestRequireRoles:
    async def test_passes_when_user_has_required_role(
        self,
        auth_dependency: AuthDependency,
        token_validator: AsyncMock,
    ) -> None:
        user = AuthenticatedUser(
            user_id="u1", session_id="s1", roles=("admin",), permissions=()
        )
        token_validator.validate.return_value = user
        guard = RequireRoles(auth=auth_dependency, roles={"admin", "super_admin"})

        request = _make_request({"Authorization": "Bearer tok"})
        result = await guard(request)

        assert result == user

    async def test_raises_insufficient_role_when_no_match(
        self,
        auth_dependency: AuthDependency,
        token_validator: AsyncMock,
    ) -> None:
        user = AuthenticatedUser(
            user_id="u1", session_id="s1", roles=("member",), permissions=()
        )
        token_validator.validate.return_value = user
        guard = RequireRoles(auth=auth_dependency, roles={"admin", "super_admin"})

        request = _make_request({"Authorization": "Bearer tok"})
        with pytest.raises(InsufficientRoleError) as exc_info:
            await guard(request)

        assert exc_info.value.required == {"admin", "super_admin"}
        assert exc_info.value.actual == ("member",)

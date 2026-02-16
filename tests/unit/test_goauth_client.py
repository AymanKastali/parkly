from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from parkly.adapters.inbound.api.auth_exceptions import AuthenticationError
from parkly.adapters.outbound.auth.goauth_client import GoAuthTokenValidator
from parkly.application.dto.authenticated_user import AuthenticatedUser


@pytest.fixture
def http_client() -> AsyncMock:
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def goauth_validator(http_client: AsyncMock) -> GoAuthTokenValidator:
    return GoAuthTokenValidator(
        base_url="http://auth-service:8080",
        http_client=http_client,
    )


class TestGoAuthTokenValidatorValidate:
    async def test_returns_authenticated_user_on_success(
        self,
        goauth_validator: GoAuthTokenValidator,
        http_client: AsyncMock,
    ) -> None:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "message": "token is valid",
            "data": {
                "user_id": "user-123",
                "session_id": "session-456",
                "roles": ["admin", "member"],
                "permissions": ["facility:read", "facility:write"],
            },
        }
        http_client.post.return_value = response

        result = await goauth_validator.validate("valid-token")

        assert isinstance(result, AuthenticatedUser)
        assert result.user_id == "user-123"
        assert result.session_id == "session-456"
        assert result.roles == ("admin", "member")
        assert result.permissions == ("facility:read", "facility:write")
        http_client.post.assert_called_once_with(
            "http://auth-service:8080/api/v1/auth/validate",
            json={"access_token": "valid-token"},
        )

    async def test_raises_authentication_error_on_401(
        self,
        goauth_validator: GoAuthTokenValidator,
        http_client: AsyncMock,
    ) -> None:
        response = AsyncMock()
        response.status_code = 401
        http_client.post.return_value = response

        with pytest.raises(AuthenticationError, match="Invalid or expired token"):
            await goauth_validator.validate("bad-token")

    async def test_raises_authentication_error_on_400(
        self,
        goauth_validator: GoAuthTokenValidator,
        http_client: AsyncMock,
    ) -> None:
        response = AsyncMock()
        response.status_code = 400
        http_client.post.return_value = response

        with pytest.raises(AuthenticationError, match="Invalid or expired token"):
            await goauth_validator.validate("malformed")

    async def test_raises_authentication_error_on_network_error(
        self,
        goauth_validator: GoAuthTokenValidator,
        http_client: AsyncMock,
    ) -> None:
        http_client.post.side_effect = httpx.ConnectError("Connection refused")

        with pytest.raises(AuthenticationError, match="Auth service unavailable"):
            await goauth_validator.validate("any-token")

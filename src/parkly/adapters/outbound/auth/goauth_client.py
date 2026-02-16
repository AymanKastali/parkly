import httpx

from parkly.adapters.inbound.api.auth_exceptions import AuthenticationError
from parkly.application.dto.authenticated_user import AuthenticatedUser
from parkly.application.port.token_validator import TokenValidator


class GoAuthTokenValidator(TokenValidator):
    def __init__(self, base_url: str, http_client: httpx.AsyncClient) -> None:
        self._validate_url = f"{base_url}/api/v1/auth/validate"
        self._http_client = http_client

    async def validate(self, token: str) -> AuthenticatedUser:
        try:
            response = await self._http_client.post(
                self._validate_url,
                json={"access_token": token},
            )
        except httpx.HTTPError as exc:
            raise AuthenticationError("Auth service unavailable") from exc

        if response.status_code != 200:
            raise AuthenticationError("Invalid or expired token")

        data = response.json()["data"]
        return AuthenticatedUser(
            user_id=data["user_id"],
            session_id=data["session_id"],
            roles=tuple(data["roles"]),
            permissions=tuple(data.get("permissions", [])),
        )

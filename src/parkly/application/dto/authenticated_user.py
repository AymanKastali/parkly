from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    session_id: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]

class AuthenticationError(Exception):
    """Raised when token validation fails (invalid, expired, or missing)."""

    code: str = "AUTHENTICATION_ERROR"

    def __init__(self, message: str = "Authentication failed") -> None:
        self.message = message
        super().__init__(message)


class MissingTokenError(AuthenticationError):
    """Raised when the Authorization header is absent or malformed."""

    code: str = "MISSING_TOKEN"

    def __init__(self) -> None:
        super().__init__("Missing or malformed Authorization header")


class InsufficientRoleError(Exception):
    """Raised when the user lacks the required role."""

    code: str = "INSUFFICIENT_ROLE"

    def __init__(self, required: set[str], actual: tuple[str, ...]) -> None:
        self.required = required
        self.actual = actual
        self.message = (
            f"Insufficient role: required one of {required}, got {set(actual)}"
        )
        super().__init__(self.message)

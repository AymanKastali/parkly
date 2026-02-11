import time
from contextvars import Token
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from ulid import ULID

from parkly.adapters.context import request_context
from parkly.application.port.logger import Logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, logger: Logger) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._logger: Logger = logger

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        trace_id: str = str(ULID())
        token: Token[dict[str, Any]] = request_context.set({"trace_id": trace_id})

        method: str = request.method
        path: str = request.url.path
        query: str = str(request.query_params) if request.query_params else ""
        client_host: str = request.client.host if request.client else ""

        self._logger.info(
            "Request started",
            extra={
                "method": method,
                "path": path,
                "query": query,
                "client": client_host,
            },
        )

        start: float = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms: float = round((time.perf_counter() - start) * 1000, 2)

        self._logger.info(
            "Request completed",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        response.headers["X-Trace-ID"] = trace_id
        request_context.reset(token)
        return response

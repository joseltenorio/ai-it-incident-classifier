# app/middleware.py

import logging
from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.request_context import reset_request_id, set_request_id

logger = logging.getLogger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Add request tracing metadata to every HTTP request.

    The middleware accepts an incoming X-Request-ID header or generates a new
    value when the client does not provide one. The ID is returned in the
    response headers and attached to log records through a context variable.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        token = set_request_id(request_id)
        request.state.request_id = request_id

        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled request error",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            raise
        else:
            elapsed_ms = int((perf_counter() - started_at) * 1000)
            response.headers["X-Request-ID"] = request_id

            logger.info(
                "HTTP request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": elapsed_ms,
                },
            )

            return response
        finally:
            reset_request_id(token)
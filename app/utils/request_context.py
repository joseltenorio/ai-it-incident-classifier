# app/utils/request_context.py

from contextvars import ContextVar, Token

_request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)


def get_request_id() -> str | None:
    """Return the request ID associated with the current execution context.

    The value is set by the request tracing middleware and can be used by
    logging utilities without passing request metadata through every function.
    """

    return _request_id_context.get()


def set_request_id(request_id: str) -> Token[str | None]:
    """Store the current request ID in a context variable."""

    return _request_id_context.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    """Reset the request ID context after a request finishes."""

    _request_id_context.reset(token)
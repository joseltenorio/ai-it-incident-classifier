# app/utils/logging.py

import logging
import sys

from app.utils.request_context import get_request_id


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every log record.

    Logs emitted outside an HTTP request receive "-" as request_id. This keeps
    the log format stable for startup messages, tests and background code.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging with a Cloud Run-friendly format.

    Cloud Run automatically captures stdout/stderr. A consistent text format
    makes local debugging and Cloud Logging inspection easier.
    """

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s "
            "[request_id=%(request_id)s] %(message)s"
        )
    )

    root_logger.addHandler(handler)
    root_logger.setLevel(level)
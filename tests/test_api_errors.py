# tests/test_api_errors.py

from app.utils.api_errors import (
    incident_history_unavailable_error,
    incident_not_found_error,
)


def test_incident_not_found_error_uses_standard_detail() -> None:
    """Verify that incident not-found errors use the standard API shape."""

    error = incident_not_found_error()

    assert error.status_code == 404
    assert error.detail["error"] == "incident_not_found"
    assert "message" in error.detail


def test_incident_history_unavailable_error_uses_standard_detail() -> None:
    """Verify that history unavailable errors use the standard API shape."""

    error = incident_history_unavailable_error()

    assert error.status_code == 503
    assert error.detail["error"] == "incident_history_unavailable"
    assert "message" in error.detail
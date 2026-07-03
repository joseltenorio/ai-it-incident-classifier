# tests/test_request_tracing.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_response_includes_generated_request_id() -> None:
    """Verify that the tracing middleware adds X-Request-ID to responses."""

    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_response_preserves_incoming_request_id() -> None:
    """Verify that caller-provided request IDs are preserved."""

    response = client.get(
        "/health",
        headers={"X-Request-ID": "test-request-id-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-id-123"
# tests/test_health.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint_returns_service_metadata() -> None:
    """Verify that the root endpoint exposes basic service metadata."""

    response = client.get("/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["service"] == "AI IT Incident Classifier"
    assert payload["status"] == "running"
    assert payload["version"] == "0.1.0"


def test_health_endpoint_returns_healthy_status() -> None:
    """Verify that the health endpoint can be used as a runtime check."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_endpoint_returns_runtime_readiness() -> None:
    """Verify that the readiness endpoint exposes runtime configuration status."""

    response = client.get("/ready")

    assert response.status_code in {200, 503}

    payload = response.json()

    assert payload["status"] in {"ready", "not_ready"}
    assert "environment" in payload
    assert "classifier_provider" in payload
    assert "bigquery_persistence_enabled" in payload
    assert "checks" in payload
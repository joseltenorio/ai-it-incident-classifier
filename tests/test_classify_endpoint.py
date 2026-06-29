# tests/test_classify_endpoint.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_classify_endpoint_returns_mock_classification() -> None:
    """Verify that the classify endpoint returns a structured response."""

    response = client.post(
        "/incidents/classify",
        json={
            "title": "No puedo conectarme a la VPN",
            "description": (
                "Desde ayer intento conectarme a la VPN de la empresa, "
                "pero aparece error de autenticación."
            ),
            "reported_by": "usuario.demo@empresa.com",
            "source_channel": "postman",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["incident_id"].startswith("INC-")
    assert payload["category"] == "VPN"
    assert payload["priority"] == "Media"
    assert payload["responsible_area"] == "Infraestructura"
    assert payload["confidence_level"] == "Media"
    assert payload["needs_human_review"] is False
    assert payload["model_name"].endswith("-mock")
    assert "created_at" in payload


def test_classify_endpoint_rejects_invalid_payload() -> None:
    """Verify that FastAPI rejects invalid incident payloads."""

    response = client.post(
        "/incidents/classify",
        json={
            "title": "VPN",
            "description": "Error",
        },
    )

    assert response.status_code == 422
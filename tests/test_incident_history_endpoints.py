# tests/test_incident_history_endpoints.py

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.services.bigquery_repository import BigQueryQueryError

client = TestClient(app)


def test_list_incidents_endpoint_returns_recent_incidents(monkeypatch) -> None:
    """Verify that the history endpoint returns compact incident records."""

    from app.api import routes_incidents

    monkeypatch.setattr(
        routes_incidents,
        "list_recent_incident_classifications",
        lambda limit=20: [
            {
                "incident_id": "INC-20260704-8E878D27",
                "title": "No puedo conectarme a la VPN",
                "category": "VPN",
                "priority": "Media",
                "responsible_area": "Infraestructura",
                "confidence_level": "Media",
                "needs_human_review": False,
                "model_name": "gemini-2.5-flash-mock",
                "created_at": datetime(2026, 7, 4, 2, 41, 24, tzinfo=UTC),
            }
        ],
    )

    response = client.get("/incidents")

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["incident_id"] == "INC-20260704-8E878D27"
    assert payload[0]["category"] == "VPN"
    assert payload[0]["priority"] == "Media"


def test_list_incidents_endpoint_accepts_limit_query_param(monkeypatch) -> None:
    """Verify that the history endpoint forwards the requested limit."""

    from app.api import routes_incidents

    captured = {}

    def fake_list_recent_incident_classifications(limit: int = 20):
        captured["limit"] = limit
        return []

    monkeypatch.setattr(
        routes_incidents,
        "list_recent_incident_classifications",
        fake_list_recent_incident_classifications,
    )

    response = client.get("/incidents?limit=5")

    assert response.status_code == 200
    assert response.json() == []
    assert captured["limit"] == 5


def test_get_incident_endpoint_returns_detail(monkeypatch) -> None:
    """Verify that the detail endpoint returns one classified incident."""

    from app.api import routes_incidents

    monkeypatch.setattr(
        routes_incidents,
        "get_incident_classification_by_id",
        lambda incident_id: {
            "incident_id": incident_id,
            "title": "No puedo conectarme a la VPN",
            "description": "Desde ayer intento conectarme a la VPN corporativa.",
            "reported_by": "usuario.demo@empresa.com",
            "source_channel": "postman",
            "category": "VPN",
            "priority": "Media",
            "responsible_area": "Infraestructura",
            "summary": "The user cannot connect to the corporate VPN.",
            "suggested_action": "Validate credentials and review VPN logs.",
            "confidence_level": "Media",
            "needs_human_review": False,
            "model_name": "gemini-2.5-flash-mock",
            "model_latency_ms": 0,
            "created_at": datetime(2026, 7, 4, 2, 41, 24, tzinfo=UTC),
        },
    )

    response = client.get("/incidents/INC-20260704-8E878D27")

    assert response.status_code == 200

    payload = response.json()

    assert payload["incident_id"] == "INC-20260704-8E878D27"
    assert payload["source_channel"] == "postman"
    assert payload["category"] == "VPN"
    assert payload["model_latency_ms"] == 0


def test_get_incident_endpoint_returns_404_when_not_found(monkeypatch) -> None:
    """Verify that missing incident IDs return a clear not-found response."""

    from app.api import routes_incidents

    monkeypatch.setattr(
        routes_incidents,
        "get_incident_classification_by_id",
        lambda incident_id: None,
    )

    response = client.get("/incidents/INC-UNKNOWN")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "incident_not_found"


def test_list_incidents_endpoint_returns_503_when_bigquery_fails(monkeypatch) -> None:
    """Verify that BigQuery query failures return a service unavailable error."""

    from app.api import routes_incidents

    def raise_query_error(limit: int = 20):
        raise BigQueryQueryError("BigQuery history query failed.")

    monkeypatch.setattr(
        routes_incidents,
        "list_recent_incident_classifications",
        raise_query_error,
    )

    response = client.get("/incidents")

    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "incident_history_unavailable"
import pytest
from pydantic import ValidationError

from app.schemas import IncidentRequest, SourceChannel


def test_incident_request_accepts_valid_payload() -> None:
    payload = IncidentRequest(
        title="No puedo conectarme a la VPN",
        description=(
            "Desde ayer intento conectarme a la VPN de la empresa, "
            "pero aparece error de autenticación."
        ),
        reported_by="usuario.demo@empresa.com",
        source_channel=SourceChannel.WEB,
    )

    assert payload.title == "No puedo conectarme a la VPN"
    assert payload.reported_by == "usuario.demo@empresa.com"
    assert payload.source_channel == SourceChannel.WEB


def test_incident_request_rejects_short_title() -> None:
    with pytest.raises(ValidationError):
        IncidentRequest(
            title="VPN",
            description="El usuario no puede conectarse a la VPN corporativa.",
        )


def test_incident_request_rejects_short_description() -> None:
    with pytest.raises(ValidationError):
        IncidentRequest(
            title="Problema de acceso VPN",
            description="Error",
        )


def test_incident_request_uses_api_as_default_source_channel() -> None:
    payload = IncidentRequest(
        title="Problema de acceso VPN",
        description="El usuario no puede conectarse a la VPN corporativa.",
    )

    assert payload.source_channel == SourceChannel.API
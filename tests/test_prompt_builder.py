# tests/test_prompt_builder.py

from app.core.prompt_builder import build_incident_classification_prompt
from app.schemas import IncidentRequest


def test_prompt_builder_includes_incident_payload() -> None:
    """Verify that the prompt includes the user incident content."""

    request = IncidentRequest(
        title="No puedo conectarme a la VPN",
        description="El cliente VPN muestra error de autenticación.",
    )

    prompt = build_incident_classification_prompt(request)

    assert "No puedo conectarme a la VPN" in prompt
    assert "El cliente VPN muestra error de autenticación." in prompt


def test_prompt_builder_includes_controlled_values() -> None:
    """Verify that the prompt includes controlled classification values."""

    request = IncidentRequest(
        title="No puedo conectarme a la VPN",
        description="El cliente VPN muestra error de autenticación.",
    )

    prompt = build_incident_classification_prompt(request)

    assert "VPN" in prompt
    assert "Redes" in prompt
    assert "Media" in prompt
    assert "Infraestructura" in prompt
    assert "needs_human_review" in prompt
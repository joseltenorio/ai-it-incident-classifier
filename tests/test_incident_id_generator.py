# tests/test_incident_id_generator.py

from datetime import UTC, datetime

from app.services.incident_id_generator import generate_incident_id


def test_generate_incident_id_uses_expected_prefix_and_date() -> None:
    """Verify that incident IDs include the INC prefix and creation date."""

    created_at = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)

    incident_id = generate_incident_id(created_at)

    assert incident_id.startswith("INC-20260629-")


def test_generate_incident_id_uses_short_random_suffix() -> None:
    """Verify that the generated suffix has the expected length."""

    created_at = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)

    incident_id = generate_incident_id(created_at)
    suffix = incident_id.split("-")[-1]

    assert len(suffix) == 8
    assert suffix.isalnum()
    assert suffix == suffix.upper()
# tests/test_catalogs.py

from app.core.catalogs import (
    ALLOWED_CATEGORIES,
    ALLOWED_CONFIDENCE_LEVELS,
    ALLOWED_PRIORITIES,
    ALLOWED_RESPONSIBLE_AREAS,
    ALLOWED_SOURCE_CHANNELS,
    PRIORITY_RULES,
    RESPONSIBLE_AREA_HINTS,
)
from app.schemas import IncidentPriority, ResponsibleArea


def test_allowed_catalogs_expose_controlled_values() -> None:
    """Verify that public catalogs include the controlled schema values."""

    assert "VPN" in ALLOWED_CATEGORIES
    assert "Media" in ALLOWED_PRIORITIES
    assert "Infraestructura" in ALLOWED_RESPONSIBLE_AREAS
    assert "Alta" in ALLOWED_CONFIDENCE_LEVELS
    assert "api" in ALLOWED_SOURCE_CHANNELS


def test_priority_rules_cover_all_priority_levels() -> None:
    """Verify that every priority level has a documented triage rule."""

    assert set(PRIORITY_RULES.keys()) == set(IncidentPriority)

    for rule in PRIORITY_RULES.values():
        assert len(rule) > 20


def test_responsible_area_hints_cover_all_support_areas() -> None:
    """Verify that every responsible area has ownership guidance."""

    assert set(RESPONSIBLE_AREA_HINTS.keys()) == set(ResponsibleArea)

    for hint in RESPONSIBLE_AREA_HINTS.values():
        assert len(hint) > 20
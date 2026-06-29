# app/services/mock_classifier.py

from app.core.catalogs import MOCK_CATEGORY_KEYWORDS
from app.schemas import (
    ConfidenceLevel,
    IncidentCategory,
    IncidentClassification,
    IncidentPriority,
    IncidentRequest,
    ResponsibleArea,
)


def classify_incident_with_mock(request: IncidentRequest) -> IncidentClassification:
    """Classify an incident with deterministic local rules.

    This mock classifier lets the API contract be tested before integrating
    Gemini. It is intentionally simple and will be replaced by the real AI
    classifier in the next project block.
    """

    combined_text = f"{request.title} {request.description}".lower()
    category = _detect_category(combined_text)

    return IncidentClassification(
        category=category,
        priority=_detect_priority(combined_text, category),
        responsible_area=_detect_responsible_area(category),
        summary=_build_summary(request, category),
        suggested_action=_build_suggested_action(category),
        confidence_level=_detect_confidence(category),
        needs_human_review=category == IncidentCategory.OTHER,
    )


def _detect_category(text: str) -> IncidentCategory:
    """Detect the most likely category using local keyword scoring.

    The mock classifier scores every category instead of returning the first
    keyword match. This avoids classifying security-related login incidents as
    generic access issues when terms like suspicious activity or MFA are present.
    """

    category_scores: dict[IncidentCategory, int] = {}

    for category, keywords in MOCK_CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)

        if score > 0:
            category_scores[category] = score

    if not category_scores:
        return IncidentCategory.OTHER

    return max(
        category_scores,
        key=lambda category: (
            category_scores[category],
            category == IncidentCategory.SECURITY,
        ),
    )


def _detect_priority(text: str, category: IncidentCategory) -> IncidentPriority:
    """Estimate priority using simple impact and risk indicators."""

    critical_terms = ("producción", "caído", "caida", "outage", "todos los usuarios", "crítico")
    high_terms = ("varios usuarios", "bloqueado", "no pueden trabajar", "urgente")

    if any(term in text for term in critical_terms):
        return IncidentPriority.CRITICAL

    if category == IncidentCategory.SECURITY:
        return IncidentPriority.HIGH

    if any(term in text for term in high_terms):
        return IncidentPriority.HIGH

    if category == IncidentCategory.OTHER:
        return IncidentPriority.MEDIUM

    return IncidentPriority.MEDIUM


def _detect_responsible_area(category: IncidentCategory) -> ResponsibleArea:
    """Map an incident category to a first responsible support area."""

    mapping = {
        IncidentCategory.VPN: ResponsibleArea.INFRASTRUCTURE,
        IncidentCategory.NETWORK: ResponsibleArea.INFRASTRUCTURE,
        IncidentCategory.ACCESS: ResponsibleArea.IT_SUPPORT,
        IncidentCategory.EMAIL: ResponsibleArea.IT_SUPPORT,
        IncidentCategory.HARDWARE: ResponsibleArea.IT_SUPPORT,
        IncidentCategory.OPERATING_SYSTEM: ResponsibleArea.IT_SUPPORT,
        IncidentCategory.DATABASE: ResponsibleArea.DATABASE,
        IncidentCategory.APPLICATIONS: ResponsibleArea.APPLICATIONS,
        IncidentCategory.SECURITY: ResponsibleArea.SECURITY,
        IncidentCategory.CLOUD: ResponsibleArea.CLOUD,
        IncidentCategory.OTHER: ResponsibleArea.IT_SUPPORT,
    }

    return mapping[category]


def _build_summary(request: IncidentRequest, category: IncidentCategory) -> str:
    """Build a short technical summary for the mocked classification."""

    return (
        f"The incident was classified as {category.value} based on the provided "
        f"title and description: {request.title}."
    )


def _build_suggested_action(category: IncidentCategory) -> str:
    """Return a first suggested support action for the detected category."""

    actions = {
        IncidentCategory.VPN: (
            "Validate user credentials, account status, VPN client configuration "
            "and VPN service logs."
        ),
        IncidentCategory.NETWORK: (
            "Check connectivity, network availability, DNS resolution and recent "
            "network changes."
        ),
        IncidentCategory.ACCESS: (
            "Validate user permissions, account status, password state and access "
            "policies."
        ),
        IncidentCategory.EMAIL: (
            "Review mailbox access, account status, mail client configuration and "
            "email service availability."
        ),
        IncidentCategory.HARDWARE: (
            "Inspect the affected device, peripherals, warranty status and possible "
            "replacement needs."
        ),
        IncidentCategory.OPERATING_SYSTEM: (
            "Review operating system logs, recent updates, startup errors and device "
            "health."
        ),
        IncidentCategory.DATABASE: (
            "Check database connectivity, query performance, locks, service health "
            "and recent deployments."
        ),
        IncidentCategory.APPLICATIONS: (
            "Review application logs, user permissions, recent releases and related "
            "backend services."
        ),
        IncidentCategory.SECURITY: (
            "Review authentication logs, MFA status, suspicious activity and apply "
            "security escalation procedures."
        ),
        IncidentCategory.CLOUD: (
            "Validate cloud IAM permissions, managed service health, deployment state "
            "and resource configuration."
        ),
        IncidentCategory.OTHER: (
            "Review the ticket manually and request more information if the incident "
            "description is not clear."
        ),
    }

    return actions[category]


def _detect_confidence(category: IncidentCategory) -> ConfidenceLevel:
    """Assign qualitative confidence for the local mock result."""

    if category == IncidentCategory.OTHER:
        return ConfidenceLevel.LOW

    return ConfidenceLevel.MEDIUM
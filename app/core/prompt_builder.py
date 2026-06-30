# app/core/prompt_builder.py

from app.core.catalogs import (
    ALLOWED_CATEGORIES,
    ALLOWED_CONFIDENCE_LEVELS,
    ALLOWED_PRIORITIES,
    ALLOWED_RESPONSIBLE_AREAS,
    PRIORITY_RULES,
    RESPONSIBLE_AREA_HINTS,
)
from app.schemas import IncidentRequest


def build_incident_classification_prompt(request: IncidentRequest) -> str:
    """Build the prompt used by Gemini to classify IT support incidents.

    The prompt includes controlled catalogs and triage rules so the model
    returns a classification aligned with the backend contract.
    """

    return f"""
You are an IT support triage analyst.

Classify the following IT support incident using only the controlled values
provided below.

Incident title:
{request.title}

Incident description:
{request.description}

Controlled categories:
{_format_values(ALLOWED_CATEGORIES)}

Controlled priorities:
{_format_values(ALLOWED_PRIORITIES)}

Responsible support areas:
{_format_values(ALLOWED_RESPONSIBLE_AREAS)}

Confidence levels:
{_format_values(ALLOWED_CONFIDENCE_LEVELS)}

Priority rules:
{_format_priority_rules()}

Responsible area hints:
{_format_responsible_area_hints()}

Return a concise classification in valid JSON using this exact structure:

{{
  "category": "one controlled category",
  "priority": "one controlled priority",
  "responsible_area": "one controlled responsible area",
  "summary": "short technical summary in English",
  "suggested_action": "first recommended support action in English",
  "confidence_level": "one controlled confidence level",
  "needs_human_review": false
}}

Rules:
- Do not invent new categories, priorities, responsible areas or confidence levels.
- Set needs_human_review to true when the incident is ambiguous, incomplete,
  risky, security-sensitive or cannot be confidently classified.
- Keep summary under 600 characters.
- Keep suggested_action under 800 characters.
- Return JSON only.
""".strip()


def _format_values(values: tuple[str, ...]) -> str:
    """Format controlled values as a compact bullet list."""

    return "\n".join(f"- {value}" for value in values)


def _format_priority_rules() -> str:
    """Format priority rules for prompt injection."""

    return "\n".join(
        f"- {priority.value}: {description}"
        for priority, description in PRIORITY_RULES.items()
    )


def _format_responsible_area_hints() -> str:
    """Format responsible area hints for prompt injection."""

    return "\n".join(
        f"- {area.value}: {description}"
        for area, description in RESPONSIBLE_AREA_HINTS.items()
    )
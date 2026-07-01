# app/services/incident_record_mapper.py

from datetime import datetime
from typing import Any

from app.schemas import IncidentClassification, IncidentRequest


def build_incident_record(
    *,
    request: IncidentRequest,
    classification: IncidentClassification,
    incident_id: str,
    model_name: str,
    model_latency_ms: int,
    raw_model_response: str,
    created_at: datetime,
) -> dict[str, Any]:
    """Build the BigQuery record for one classified incident.

    The API response contains the user-facing classification. The BigQuery
    record keeps the original incident, model metadata and raw model response
    so the classification can be audited later.
    """

    return {
        "incident_id": incident_id,
        "title": request.title,
        "description": request.description,
        "reported_by": request.reported_by,
        "source_channel": request.source_channel.value,
        "category": classification.category.value,
        "priority": classification.priority.value,
        "responsible_area": classification.responsible_area.value,
        "summary": classification.summary,
        "suggested_action": classification.suggested_action,
        "confidence_level": classification.confidence_level.value,
        "needs_human_review": classification.needs_human_review,
        "model_name": model_name,
        "model_latency_ms": model_latency_ms,
        "raw_model_response": raw_model_response,
        "created_at": created_at.isoformat(),
    }
# app/services/incident_history_mapper.py

from collections.abc import Mapping
from typing import Any

from app.schemas import IncidentDetailResponse, IncidentHistoryItem


def build_incident_history_item(record: Mapping[str, Any]) -> IncidentHistoryItem:
    """Build a compact incident history response from a BigQuery record."""

    return IncidentHistoryItem.model_validate(dict(record))


def build_incident_detail_response(
    record: Mapping[str, Any],
) -> IncidentDetailResponse:
    """Build a detailed incident response from a BigQuery record.

    The mapper keeps route handlers small and ensures BigQuery rows are
    converted through the same Pydantic contract used by FastAPI responses.
    """

    return IncidentDetailResponse.model_validate(dict(record))
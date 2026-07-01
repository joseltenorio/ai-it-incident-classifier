# app/services/bigquery_repository.py

import logging
from collections.abc import Mapping
from typing import Any

from google.cloud import bigquery

from app.config import settings

logger = logging.getLogger(__name__)


class BigQueryPersistenceError(RuntimeError):
    """Raised when an incident classification cannot be persisted in BigQuery."""


def insert_incident_classification(record: Mapping[str, Any]) -> None:
    """Insert one classified incident record into BigQuery.

    The repository uses insert_rows_json because the API receives one incident
    at a time and needs near-real-time operational traceability.
    """

    table_id = settings.bigquery_table_id

    if not table_id:
        raise BigQueryPersistenceError(
            "GOOGLE_CLOUD_PROJECT is required to persist records in BigQuery."
        )

    client = bigquery.Client(project=settings.google_cloud_project)

    try:
        errors = client.insert_rows_json(table_id, [dict(record)])
    except Exception as exc:
        logger.exception("BigQuery insert request failed.")
        raise BigQueryPersistenceError("BigQuery insert request failed.") from exc

    if errors:
        logger.error("BigQuery rejected the incident record: %s", errors)
        raise BigQueryPersistenceError(f"BigQuery insert returned errors: {errors}")
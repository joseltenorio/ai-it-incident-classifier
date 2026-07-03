# app/services/bigquery_repository.py

import logging
from collections.abc import Mapping
from typing import Any

from google.cloud import bigquery

from app.config import settings

logger = logging.getLogger(__name__)


class BigQueryRepositoryError(RuntimeError):
    """Base error raised by the BigQuery repository."""


class BigQueryPersistenceError(BigQueryRepositoryError):
    """Raised when an incident classification cannot be persisted in BigQuery."""


class BigQueryQueryError(BigQueryRepositoryError):
    """Raised when incident history cannot be queried from BigQuery."""


def insert_incident_classification(record: Mapping[str, Any]) -> None:
    """Insert one classified incident record into BigQuery.

    The repository uses insert_rows_json because the API receives one incident
    at a time and needs near-real-time operational traceability.
    """

    table_id = _get_table_id_or_raise()

    client = bigquery.Client(project=settings.google_cloud_project)

    try:
        errors = client.insert_rows_json(table_id, [dict(record)])
    except Exception as exc:
        logger.exception("BigQuery insert request failed.")
        raise BigQueryPersistenceError("BigQuery insert request failed.") from exc

    if errors:
        logger.error("BigQuery rejected the incident record: %s", errors)
        raise BigQueryPersistenceError(f"BigQuery insert returned errors: {errors}")


def list_recent_incident_classifications(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent classified incidents from BigQuery.

    The query only returns fields needed by the history list endpoint so the
    response remains compact and efficient.
    """

    table_id = _get_table_id_or_raise()
    client = bigquery.Client(project=settings.google_cloud_project)

    query = f"""
        SELECT
          incident_id,
          title,
          category,
          priority,
          responsible_area,
          confidence_level,
          needs_human_review,
          model_name,
          created_at
        FROM `{table_id}`
        ORDER BY created_at DESC
        LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        rows = client.query(query, job_config=job_config).result()
    except Exception as exc:
        logger.exception("BigQuery history query failed.")
        raise BigQueryQueryError("BigQuery history query failed.") from exc

    return [_row_to_dict(row) for row in rows]


def get_incident_classification_by_id(incident_id: str) -> dict[str, Any] | None:
    """Return a classified incident by ID from BigQuery.

    The detail endpoint exposes the stored incident and model metadata, but it
    does not expose raw_model_response to keep the public API focused.
    """

    table_id = _get_table_id_or_raise()
    client = bigquery.Client(project=settings.google_cloud_project)

    query = f"""
        SELECT
          incident_id,
          title,
          description,
          reported_by,
          source_channel,
          category,
          priority,
          responsible_area,
          summary,
          suggested_action,
          confidence_level,
          needs_human_review,
          model_name,
          model_latency_ms,
          created_at
        FROM `{table_id}`
        WHERE incident_id = @incident_id
        LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("incident_id", "STRING", incident_id),
        ]
    )

    try:
        rows = list(client.query(query, job_config=job_config).result())
    except Exception as exc:
        logger.exception("BigQuery incident lookup failed.")
        raise BigQueryQueryError("BigQuery incident lookup failed.") from exc

    if not rows:
        return None

    return _row_to_dict(rows[0])


def _get_table_id_or_raise() -> str:
    """Return the configured BigQuery table ID or fail with a repository error."""

    table_id = settings.bigquery_table_id

    if not table_id:
        raise BigQueryRepositoryError(
            "GOOGLE_CLOUD_PROJECT is required to use BigQuery repository operations."
        )

    return table_id


def _row_to_dict(row: Any) -> dict[str, Any]:
    """Convert a BigQuery Row object into a plain dictionary."""

    return dict(row.items())
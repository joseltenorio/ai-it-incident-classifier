# tests/test_bigquery_repository.py

import pytest

from app.services.bigquery_repository import (
    BigQueryRepositoryError,
    insert_incident_classification,
    list_recent_incident_classifications,
)


def test_insert_incident_classification_requires_project(monkeypatch) -> None:
    """Verify that BigQuery persistence requires a configured project."""

    from app.services import bigquery_repository

    monkeypatch.setattr(bigquery_repository.settings, "google_cloud_project", None)

    with pytest.raises(BigQueryRepositoryError):
        insert_incident_classification({"incident_id": "INC-20260701-ABC12345"})


def test_list_recent_incident_classifications_requires_project(monkeypatch) -> None:
    """Verify that BigQuery history queries require a configured project."""

    from app.services import bigquery_repository

    monkeypatch.setattr(bigquery_repository.settings, "google_cloud_project", None)

    with pytest.raises(BigQueryRepositoryError):
        list_recent_incident_classifications()
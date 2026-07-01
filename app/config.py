# app/config.py

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class ClassifierProvider(StrEnum):
    """Supported classifier providers for incident triage."""

    MOCK = "mock"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    This class centralizes runtime configuration so the application can run
    consistently in local development, Docker and Cloud Run.
    """

    # Application metadata used by FastAPI and health/root endpoints.
    app_name: str = "AI IT Incident Classifier"
    app_version: str = "0.1.0"
    environment: str = "local"

    # Classifier provider.
    # mock keeps local development deterministic, while gemini enables the
    # real generative AI classifier when the API key is configured.
    classifier_provider: ClassifierProvider = ClassifierProvider.MOCK

    # BigQuery persistence is disabled by default so tests and local API
    # contract validation can run without Google Cloud credentials.
    enable_bigquery_persistence: bool = False

    # Google Cloud and BigQuery settings.
    # google_cloud_project is optional while persistence is disabled.
    google_cloud_project: str | None = None
    bigquery_dataset: str = "ai_operations"
    bigquery_table: str = "incident_classifications"

    # Gemini settings.
    # The API key is required only when classifier_provider is set to gemini.
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # Pydantic settings configuration.
    # Local values are loaded from .env, while Cloud Run will provide the same
    # values as environment variables configured at deployment time.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_local(self) -> bool:
        """Return True when the application is running in local mode."""
        return self.environment.lower() == "local"

    @property
    def use_gemini_classifier(self) -> bool:
        """Return True when the configured classifier provider is Gemini."""
        return self.classifier_provider == ClassifierProvider.GEMINI

    @property
    def bigquery_table_id(self) -> str | None:
        """Build the fully qualified BigQuery table ID.

        BigQuery expects table references in this format:
        project_id.dataset_id.table_id

        If the Google Cloud project is not configured yet, None is returned
        so local development can continue without requiring BigQuery access.
        """
        if not self.google_cloud_project:
            return None

        return (
            f"{self.google_cloud_project}."
            f"{self.bigquery_dataset}."
            f"{self.bigquery_table}"
        )


# A single settings instance is imported across the application.
# This avoids reloading environment variables in every module.
settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    This class centralizes runtime configuration so the application can run
    consistently in local development, Docker and Cloud Run.
    """

    # Application metadata used by FastAPI and health/root endpoints.
    app_name: str = "AI IT Incident Classifier"
    app_version: str = "0.1.0"
    environment: str = "local"

    # Google Cloud and BigQuery settings.
    # google_cloud_project is optional in local mode because some features
    # can run without connecting to Google Cloud during early development.
    google_cloud_project: str | None = None
    bigquery_dataset: str = "ai_operations"
    bigquery_table: str = "incident_classifications"

    # Gemini settings.
    # The API key will be required once the real AI classifier is integrated.
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

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
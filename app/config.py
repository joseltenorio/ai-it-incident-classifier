# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Default values allow the API to run locally without requiring a .env file.
    """

    app_name: str = "AI IT Incident Classifier"
    app_version: str = "0.1.0"
    environment: str = "local"

    # SettingsConfigDict tells Pydantic where to load local environment values from.
    # In Cloud Run, values will come directly from configured environment variables.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# A single settings instance is imported by the rest of the application.
settings = Settings()
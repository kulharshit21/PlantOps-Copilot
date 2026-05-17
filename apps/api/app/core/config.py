from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PlantOps Copilot API"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: SecretStr | None = Field(
        default=None,
        alias="SUPABASE_SERVICE_ROLE_KEY",
    )
    supabase_jwt_secret: SecretStr | None = Field(default=None, alias="SUPABASE_JWT_SECRET")
    model_artifact_path: str = Field(default="./ml/artifacts/failure_model.joblib", alias="MODEL_ARTIFACT_PATH")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("cors_origins")
    @classmethod
    def reject_wildcard_origins(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ORIGINS must not contain wildcard origins")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

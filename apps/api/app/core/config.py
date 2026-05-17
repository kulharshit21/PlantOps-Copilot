from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PlantOps Copilot API"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: SecretStr | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: SecretStr | None = Field(
        default=None,
        alias="SUPABASE_SERVICE_ROLE_KEY",
    )
    supabase_jwt_secret: SecretStr | None = Field(default=None, alias="SUPABASE_JWT_SECRET")
    supabase_jwks_url: str | None = Field(default=None, alias="SUPABASE_JWKS_URL")
    model_artifact_path: str = Field(default="./ml/artifacts/failure_model.joblib", alias="MODEL_ARTIFACT_PATH")
    mistral_api_key: SecretStr | None = Field(default=None, alias="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-large-latest", alias="MISTRAL_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_llm_model: str = Field(default="gemma4:e4b", alias="OLLAMA_LLM_MODEL")
    ollama_embedding_model: str = Field(default="embeddinggemma", alias="OLLAMA_EMBEDDING_MODEL")
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

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    def validate_startup_security(self) -> None:
        if self.is_production and self.demo_mode:
            raise ValueError("DEMO_MODE must be false when APP_ENV=production")

        if not self.demo_mode:
            missing: list[str] = []
            if not self.supabase_url:
                missing.append("SUPABASE_URL")
            if self.supabase_anon_key is None:
                missing.append("SUPABASE_ANON_KEY")
            if self.supabase_service_role_key is None:
                missing.append("SUPABASE_SERVICE_ROLE_KEY")
            if missing:
                joined = ", ".join(missing)
                raise ValueError(f"Live mode requires backend auth/data settings: {joined}")


@lru_cache
def get_settings() -> Settings:
    return Settings()

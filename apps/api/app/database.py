from dataclasses import dataclass

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class DatabaseConnectionSettings:
    supabase_url: str
    service_role_key: str


class MissingDatabaseConfigurationError(RuntimeError):
    pass


def get_database_connection_settings(
    settings: Settings | None = None,
) -> DatabaseConnectionSettings:
    active_settings = settings or get_settings()
    if not active_settings.supabase_url:
        raise MissingDatabaseConfigurationError("SUPABASE_URL is not configured")
    if active_settings.supabase_service_role_key is None:
        raise MissingDatabaseConfigurationError(
            "SUPABASE_SERVICE_ROLE_KEY is not configured"
        )

    return DatabaseConnectionSettings(
        supabase_url=active_settings.supabase_url,
        service_role_key=active_settings.supabase_service_role_key.get_secret_value(),
    )

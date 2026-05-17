import pytest
from pydantic import SecretStr

from app.config import Settings
from app.database import (
    MissingDatabaseConfigurationError,
    get_database_connection_settings,
)


def test_database_settings_require_backend_only_supabase_values() -> None:
    settings = Settings(
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY=SecretStr("server-only-placeholder"),
    )

    connection = get_database_connection_settings(settings)

    assert connection.supabase_url == "https://example.supabase.co"
    assert connection.service_role_key == "server-only-placeholder"


def test_database_settings_fail_closed_without_service_key() -> None:
    settings = Settings(SUPABASE_URL="https://example.supabase.co")

    with pytest.raises(MissingDatabaseConfigurationError):
        get_database_connection_settings(settings)

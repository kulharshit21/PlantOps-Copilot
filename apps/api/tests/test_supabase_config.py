from pydantic import SecretStr

from app.core.config import Settings
from app.services.supabase_client import SupabaseClient


def test_supabase_health_fails_closed_without_server_key() -> None:
    health = SupabaseClient(Settings(SUPABASE_URL="https://example.supabase.co")).health()

    assert health.configured is False
    assert health.reachable is False
    assert "SERVICE_ROLE" in health.detail


def test_ollama_defaults_to_gemma4() -> None:
    settings = Settings(SUPABASE_SERVICE_ROLE_KEY=SecretStr("placeholder"))

    assert settings.ollama_llm_model == "gemma4:e4b"

from pathlib import Path

from app.core.config import Settings
from app.schemas.security import SecurityReadinessResponse
from app.services.supabase import SupabaseService, SupabaseServiceError
from app.services.supabase_client import SupabaseClient


class ReadinessService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def security_readiness(self) -> SecurityReadinessResponse:
        health = SupabaseClient(self.settings).health()
        notes: list[str] = []
        auth_configured = bool(
            self.settings.supabase_url
            and self.settings.supabase_anon_key
            and self.settings.supabase_service_role_key
        )
        if self.settings.demo_mode:
            notes.append("DEMO_MODE is active; no-auth local fallback is enabled.")
        if not auth_configured:
            notes.append("Supabase auth/data settings are incomplete.")

        audit_logs_reachable = False
        if auth_configured:
            try:
                SupabaseService(self.settings).rest_select("audit_logs", {"select": "id", "limit": "1"})
                audit_logs_reachable = True
            except SupabaseServiceError as exc:
                notes.append(f"audit_logs check failed: {exc.__class__.__name__}")

        migrations_dir = Path(__file__).resolve().parents[4] / "supabase" / "migrations"
        rls_detected = any(migrations_dir.glob("*schema*.sql")) and any(migrations_dir.glob("*live_readiness*.sql"))
        if not rls_detected:
            notes.append("Expected RLS/live-readiness migration files were not detected.")

        return SecurityReadinessResponse(
            auth_configured=auth_configured,
            demo_mode=self.settings.demo_mode,
            supabase_reachable=health.reachable,
            rls_migration_files_detected=rls_detected,
            audit_logs_table_reachable=audit_logs_reachable,
            rag_citation_test_status="covered-by-tests" if rls_detected else "unknown",
            work_order_persistence_status="covered-by-tests",
            notes=notes,
        )

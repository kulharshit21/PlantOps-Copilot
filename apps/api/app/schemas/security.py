from pydantic import BaseModel


class SecurityReadinessResponse(BaseModel):
    auth_configured: bool
    demo_mode: bool
    supabase_reachable: bool
    rls_migration_files_detected: bool
    audit_logs_table_reachable: bool
    rag_citation_test_status: str
    work_order_persistence_status: str
    notes: list[str]

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.core.logging import mask_sensitive_values


@dataclass(frozen=True)
class AuditEvent:
    actor_id: str
    action: str
    resource_type: str
    resource_id: str | None
    metadata: dict[str, Any]
    created_at: str


class AuditLogService:
    def record(
        self,
        *,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        return AuditEvent(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=mask_sensitive_values(metadata or {}),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

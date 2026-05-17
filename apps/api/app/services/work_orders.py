from uuid import uuid4

from fastapi import HTTPException, status

from app.core.security import CurrentUser, UserRole
from app.schemas.work_orders import WorkOrderCreate, WorkOrderRead, WorkOrderTransition


class WorkOrderService:
    def __init__(self) -> None:
        self._orders: dict[str, WorkOrderRead] = {}

    def list(self, user: CurrentUser) -> list[WorkOrderRead]:
        _ = user
        return list(self._orders.values()) or [
            WorkOrderRead(
                id="wo-spindle-inspection",
                asset_id="asset-line-2-spindle",
                title="Inspect Line 2 spindle vibration",
                status="draft",
                priority="high",
                assigned_role="reliability_engineer",
                description="Demo draft generated from cited triage evidence.",
                audit_events=["created:draft"],
            )
        ]

    def create(self, request: WorkOrderCreate, user: CurrentUser) -> WorkOrderRead:
        self._require_any(user, {UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin})
        order = WorkOrderRead(
            id=f"wo-{uuid4().hex[:8]}",
            asset_id=request.asset_id,
            title=request.title,
            status="draft",
            priority=request.priority,
            assigned_role="reliability_engineer",
            description=request.recommended_action,
            audit_events=[f"{user.role.value}:created_draft"],
        )
        self._orders[order.id] = order
        return order

    def transition(self, order_id: str, request: WorkOrderTransition, user: CurrentUser) -> WorkOrderRead:
        order = self._orders.get(order_id)
        if order is None:
            order = self.list(user)[0]
        if request.status in {"approved", "assigned", "closed"}:
            self._require_any(user, {UserRole.supervisor, UserRole.admin})
        elif request.status == "review":
            self._require_any(user, {UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin})
        updated = order.model_copy(
            update={
                "status": request.status,
                "audit_events": [*order.audit_events, f"{user.role.value}:{request.status}:{request.note}"],
            }
        )
        self._orders[updated.id] = updated
        return updated

    def _require_any(self, user: CurrentUser, allowed: set[UserRole]) -> None:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")


WORK_ORDER_SERVICE = WorkOrderService()

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, UserRole, require_roles
from app.schemas.work_orders import WorkOrderCreate, WorkOrderRead
from app.services.audit import AuditLogService
from app.services.demo_data import DEMO_WORK_ORDERS

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


@router.get("", response_model=list[WorkOrderRead])
def list_work_orders(
    user: CurrentUser = Depends(require_roles(UserRole.technician, UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
) -> list[WorkOrderRead]:
    _ = user
    return DEMO_WORK_ORDERS


@router.post("", response_model=WorkOrderRead)
def create_work_order(
    request: WorkOrderCreate,
    user: CurrentUser = Depends(require_roles(UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
) -> WorkOrderRead:
    AuditLogService().record(
        actor_id=user.user_id,
        action="work_order.create_draft",
        resource_type="work_order",
        metadata=request.model_dump(),
    )
    return WorkOrderRead(
        id="wo-draft-demo",
        asset_id=request.asset_id,
        title=request.title,
        status="draft",
        priority=request.priority,
        assigned_role="reliability_engineer",
    )

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, UserRole, require_roles
from app.schemas.work_orders import WorkOrderCreate, WorkOrderRead, WorkOrderTransition
from app.services.audit import AuditLogService
from app.services.work_orders import WORK_ORDER_SERVICE

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


@router.get("", response_model=list[WorkOrderRead])
def list_work_orders(
    user: CurrentUser = Depends(require_roles(UserRole.technician, UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
) -> list[WorkOrderRead]:
    return WORK_ORDER_SERVICE.list(user)


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
    return WORK_ORDER_SERVICE.create(request, user)


@router.patch("/{order_id}", response_model=WorkOrderRead)
def transition_work_order(
    order_id: str,
    request: WorkOrderTransition,
    user: CurrentUser = Depends(require_roles(UserRole.technician, UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
) -> WorkOrderRead:
    updated = WORK_ORDER_SERVICE.transition(order_id, request, user)
    AuditLogService().record(
        actor_id=user.user_id,
        action=f"work_order.{request.status}",
        resource_type="work_order",
        resource_id=updated.id,
        metadata={"note": request.note},
    )
    return updated

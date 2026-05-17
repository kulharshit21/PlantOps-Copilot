from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, UserRole, require_roles
from app.schemas.work_orders import WorkOrderCreate, WorkOrderRead, WorkOrderTransition
from app.services.audit import AuditLogService
from app.services.metrics import METRICS
from app.services.supabase import SupabaseService, SupabaseServiceError
from app.services.work_orders import WORK_ORDER_SERVICE

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


@router.get("", response_model=list[WorkOrderRead])
def list_work_orders(
    user: CurrentUser = Depends(require_roles(UserRole.technician, UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
    settings: Settings = Depends(get_settings),
) -> list[WorkOrderRead]:
    try:
        return SupabaseService(settings).list_work_orders(user)
    except SupabaseServiceError as exc:
        if settings.demo_mode:
            return WORK_ORDER_SERVICE.list(user)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase work orders data is unavailable",
        ) from exc


@router.post("", response_model=WorkOrderRead)
def create_work_order(
    request: WorkOrderCreate,
    user: CurrentUser = Depends(require_roles(UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
    settings: Settings = Depends(get_settings),
) -> WorkOrderRead:
    try:
        service = SupabaseService(settings)
        order = service.create_work_order(
            user,
            asset_id=request.asset_id,
            title=request.title,
            description=request.recommended_action,
            priority=request.priority,
            ai_recommendation={"recommended_action": request.recommended_action},
        )
        service.create_audit_log(
            user,
            action="work_order.create_draft",
            entity_type="work_order",
            entity_id=order.id,
            details=request.model_dump(),
        )
        METRICS.record_work_order_action()
        return order
    except SupabaseServiceError as exc:
        if not settings.demo_mode:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase work order creation is unavailable",
            ) from exc

        AuditLogService().record(
            actor_id=user.user_id,
            action="work_order.create_draft",
            resource_type="work_order",
            metadata=request.model_dump(),
        )
        order = WORK_ORDER_SERVICE.create(request, user)
        METRICS.record_work_order_action()
        return order


@router.patch("/{order_id}", response_model=WorkOrderRead)
def transition_work_order(
    order_id: str,
    request: WorkOrderTransition,
    user: CurrentUser = Depends(require_roles(UserRole.technician, UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin)),
    settings: Settings = Depends(get_settings),
) -> WorkOrderRead:
    if request.status in {"approved", "assigned", "closed"} and user.role not in {UserRole.supervisor, UserRole.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supervisor/admin role required")
    if request.status == "review" and user.role not in {UserRole.reliability_engineer, UserRole.supervisor, UserRole.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reliability engineer role required")

    try:
        service = SupabaseService(settings)
        updated = service.update_work_order(user, order_id=order_id, status=request.status, note=request.note)
    except SupabaseServiceError as exc:
        if not settings.demo_mode:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase work order update is unavailable",
            ) from exc

        updated = WORK_ORDER_SERVICE.transition(order_id, request, user)
        AuditLogService().record(
            actor_id=user.user_id,
            action=f"work_order.{request.status}",
            resource_type="work_order",
            resource_id=updated.id,
            metadata={"note": request.note},
        )
        METRICS.record_work_order_action()
        return updated

    service.create_audit_log(
        user,
        action=f"work_order.{request.status}",
        entity_type="work_order",
        entity_id=updated.id,
        details={"note": request.note},
    )
    METRICS.record_work_order_action()
    return updated

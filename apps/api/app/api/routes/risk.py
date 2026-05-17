from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.risk import RiskPredictRequest, RiskPredictResponse
from app.services.audit import AuditLogService
from app.services.risk import RiskService

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/predict", response_model=RiskPredictResponse)
def predict_risk(
    request: RiskPredictRequest,
    user: CurrentUser = Depends(get_current_user),
) -> RiskPredictResponse:
    AuditLogService().record(
        actor_id=user.user_id,
        action="risk.predict",
        resource_type="asset",
        resource_id=request.asset_id,
        metadata={"asset_id": request.asset_id},
    )
    return RiskService().predict(request)

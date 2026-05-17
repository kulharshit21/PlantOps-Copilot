from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.risk import RiskPredictRequest, RiskPredictResponse
from app.services.audit import AuditLogService
from app.services.risk import RiskService
from app.services.supabase import SupabaseService, SupabaseServiceError

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/predict", response_model=RiskPredictResponse)
def predict_risk(
    request: RiskPredictRequest,
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> RiskPredictResponse:
    response = RiskService().predict(request)
    try:
        SupabaseService(settings).create_model_prediction(
            user,
            asset_id=request.asset_id,
            model_version=response.model_version,
            risk_score=response.risk_score,
            predicted_label=response.risk_level,
            features=request.model_dump(),
            explanation={
                "likely_failure_modes": response.likely_failure_modes,
                "top_features": response.top_features,
                "warning": response.warning,
            },
        )
    except SupabaseServiceError:
        if settings.demo_mode:
            AuditLogService().record(
                actor_id=user.user_id,
                action="risk.predict",
                resource_type="asset",
                resource_id=request.asset_id,
                metadata={"asset_id": request.asset_id},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase model prediction persistence is unavailable",
            )
    return response

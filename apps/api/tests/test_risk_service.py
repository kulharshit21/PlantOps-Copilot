from app.schemas.risk import RiskPredictRequest
from app.services.risk import RiskService


def test_risk_service_returns_demo_warning_without_artifact() -> None:
    response = RiskService().predict(
        RiskPredictRequest(
            asset_id="asset-line-2-spindle",
            torque_nm=100,
            tool_wear_min=210,
            vibration_mm_s=9,
            temperature_c=75,
        )
    )

    assert response.risk_score > 0
    assert response.warning == "Demo heuristic until trained ML artifact is available."
    assert response.top_features

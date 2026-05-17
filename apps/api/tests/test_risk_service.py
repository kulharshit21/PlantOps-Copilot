from app.schemas.risk import RiskPredictRequest
from app.services.risk import RiskService
from fastapi.testclient import TestClient

import app.api.routes.risk as risk_route
from app.main import app


client = TestClient(app)


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


class RecordingRiskSupabaseService:
    predictions: list[dict] = []

    def __init__(self, settings) -> None:
        self.settings = settings

    def create_model_prediction(self, user, **kwargs) -> None:
        self.predictions.append({"user": user.user_id, **kwargs})


def test_risk_endpoint_persists_model_prediction(monkeypatch) -> None:
    RecordingRiskSupabaseService.predictions = []
    monkeypatch.setattr(risk_route, "SupabaseService", RecordingRiskSupabaseService)

    response = client.post(
        "/risk/predict",
        json={
            "asset_id": "asset-line-2-spindle",
            "torque_nm": 100,
            "tool_wear_min": 210,
            "vibration_mm_s": 9,
            "temperature_c": 75,
        },
    )

    assert response.status_code == 200
    assert RecordingRiskSupabaseService.predictions[0]["asset_id"] == "asset-line-2-spindle"
    assert RecordingRiskSupabaseService.predictions[0]["model_version"]

from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.schemas.risk import RiskPredictRequest, RiskPredictResponse


FEATURE_COLUMNS = ["torque_nm", "tool_wear_min", "vibration_mm_s", "temperature_c"]


class RiskService:
    def predict(self, request: RiskPredictRequest) -> RiskPredictResponse:
        artifact_response = self._predict_with_artifact(request)
        if artifact_response is not None:
            return artifact_response

        torque_signal = min(request.torque_nm / 120.0, 1.0)
        wear_signal = min(request.tool_wear_min / 240.0, 1.0)
        vibration_signal = min(request.vibration_mm_s / 12.0, 1.0)
        temperature_signal = min(max((request.temperature_c - 35.0) / 80.0, 0.0), 1.0)
        score = round(
            0.30 * torque_signal
            + 0.30 * wear_signal
            + 0.25 * vibration_signal
            + 0.15 * temperature_signal,
            3,
        )

        if score >= 0.8:
            level = "critical"
        elif score >= 0.6:
            level = "high"
        elif score >= 0.35:
            level = "watch"
        else:
            level = "low"

        return RiskPredictResponse(
            risk_score=score,
            risk_level=level,
            likely_failure_modes=["bearing wear", "tool holder runout"],
            top_features=["torque_nm", "tool_wear_min", "vibration_mm_s"],
            model_version="heuristic-demo-v0",
            warning="Demo heuristic until trained ML artifact is available.",
        )

    def _predict_with_artifact(self, request: RiskPredictRequest) -> RiskPredictResponse | None:
        settings = get_settings()
        artifact_path = Path(settings.model_artifact_path)
        if not artifact_path.exists():
            return None

        try:
            import joblib
        except ImportError:
            return None

        bundle: dict[str, Any] = joblib.load(artifact_path)
        model = bundle["model"]
        feature_columns: list[str] = bundle.get("feature_columns", FEATURE_COLUMNS)
        feature_values = {
            "torque_nm": request.torque_nm,
            "tool_wear_min": request.tool_wear_min,
            "vibration_mm_s": request.vibration_mm_s,
            "temperature_c": request.temperature_c,
            "air_temperature_k": request.temperature_c + 273.15,
            "process_temperature_k": request.temperature_c + 278.15,
            "rotational_speed_rpm": max(800.0, 1800.0 - request.torque_nm * 4),
        }
        row = [[feature_values[column] for column in feature_columns]]
        probability = float(model.predict_proba(row)[0][1])
        score = round(max(0.0, min(probability, 1.0)), 3)
        level = "critical" if score >= 0.8 else "high" if score >= 0.6 else "watch" if score >= 0.35 else "low"
        return RiskPredictResponse(
            risk_score=score,
            risk_level=level,
            likely_failure_modes=["tool wear failure", "heat dissipation failure"],
            top_features=feature_columns[:3],
            model_version=bundle.get("model_version", "unknown-model"),
            warning="Model artifact loaded locally." if bundle.get("fallback_data_used") else None,
        )

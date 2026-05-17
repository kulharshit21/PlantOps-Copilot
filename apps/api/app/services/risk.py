from app.schemas.risk import RiskPredictRequest, RiskPredictResponse


class RiskService:
    def predict(self, request: RiskPredictRequest) -> RiskPredictResponse:
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

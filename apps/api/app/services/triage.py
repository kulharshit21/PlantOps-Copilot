from app.core.security import CurrentUser
from app.schemas.documents import RagAskRequest
from app.schemas.risk import RiskPredictRequest
from app.schemas.triage import DraftedWorkOrder, TriageRunRequest, TriageRunResponse
from app.services.rag import RagService
from app.services.risk import RiskService


class TriageWorkflow:
    def run(self, request: TriageRunRequest, user: CurrentUser) -> TriageRunResponse:
        rag = RagService().ask(
            RagAskRequest(question=request.question, top_k=4),
            user,
        )
        risk = RiskService().predict(
            RiskPredictRequest(
                asset_id=request.asset_id,
                torque_nm=request.telemetry.torque_nm,
                tool_wear_min=request.telemetry.tool_wear_min,
                vibration_mm_s=request.telemetry.vibration_mm_s,
                temperature_c=request.telemetry.temperature_c,
            )
        )
        likely_failure = risk.likely_failure_modes[0] if risk.likely_failure_modes else "unknown failure mode"
        actions = [
            rag.recommendation,
            "Attach current telemetry and cited SOP chunks to the work order.",
            "Assign reliability engineer review before restart.",
        ]
        safety_checks = [
            "Apply lockout/tagout before spindle housing inspection.",
            "Verify zero-energy state before removing guards.",
            "Escalate to supervisor if vibration remains above threshold after tool replacement.",
        ]
        return TriageRunResponse(
            issue_summary=(
                "Line 2 spindle shows elevated torque, rising tool wear, and vibration. "
                f"Risk model reports {risk.risk_level} risk."
            ),
            urgency=risk.risk_level,
            risk_score=risk.risk_score,
            likely_failure_mode=likely_failure,
            recommended_actions=actions,
            safety_checks=safety_checks,
            parts_tools_needed=["dial indicator", "vibration meter", "lubrication kit", "replacement tool holder"],
            drafted_work_order=DraftedWorkOrder(
                title="Inspect Line 2 spindle vibration and tool wear",
                priority="urgent" if risk.risk_score >= 0.8 else "high",
                description=(
                    "Inspect spindle runout, lubrication, bearing noise, and tool holder condition. "
                    "Record torque, vibration, tool-wear, and temperature readings before restart."
                ),
                acceptance_criteria=[
                    "Runout measured and documented.",
                    "Lockout/tagout checklist completed.",
                    "Bearing inspection decision recorded.",
                    "Post-inspection vibration reading below watch threshold.",
                ],
            ),
            citations=rag.citations,
            model_used=f"{rag.model_used}+{risk.model_version}",
        )

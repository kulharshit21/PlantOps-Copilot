from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser
from app.schemas.assets import AssetRead
from app.schemas.documents import RagAskRequest, RagAskResponse
from app.schemas.risk import RiskPredictRequest, RiskPredictResponse
from app.schemas.triage import DraftedWorkOrder, TriageRunRequest, TriageRunResponse
from app.services.rag import RagService
from app.services.risk import RiskService
from app.services.supabase import SupabaseService, SupabaseServiceError


@dataclass(frozen=True)
class ClassifiedIntent:
    intent: str
    requires_work_order: bool


class IntentClassifier:
    def classify(self, request: TriageRunRequest) -> ClassifiedIntent:
        text = f"{request.question} {request.incident_notes or ''}".lower()
        requires_work_order = any(marker in text for marker in ["vibration", "wear", "torque", "inspect", "failure"])
        return ClassifiedIntent(intent="maintenance_triage", requires_work_order=requires_work_order)


class RetrievalAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def retrieve(self, request: TriageRunRequest, user: CurrentUser) -> RagAskResponse:
        return RagService(self.settings).ask(
            RagAskRequest(question=request.question, plant_id=user.plant_id, top_k=4),
            user,
        )


class RiskScoringTool:
    def score(self, request: TriageRunRequest) -> RiskPredictResponse:
        return RiskService().predict(
            RiskPredictRequest(
                asset_id=request.asset_id,
                torque_nm=request.telemetry.torque_nm,
                tool_wear_min=request.telemetry.tool_wear_min,
                vibration_mm_s=request.telemetry.vibration_mm_s,
                temperature_c=request.telemetry.temperature_c,
            )
        )


class ActionPlanner:
    def plan(self, rag: RagAskResponse, risk: RiskPredictResponse) -> tuple[list[str], list[str], list[str]]:
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
        parts_tools = ["dial indicator", "vibration meter", "lubrication kit", "replacement tool holder"]
        if risk.risk_score >= 0.8:
            actions.insert(0, "Pause noncritical production until inspection is complete.")
        return actions, safety_checks, parts_tools


class WorkOrderDraftAgent:
    def draft(self, asset: AssetRead | None, risk: RiskPredictResponse) -> DraftedWorkOrder:
        asset_name = asset.name if asset else "selected asset"
        return DraftedWorkOrder(
            title=f"Inspect {asset_name} vibration and tool wear",
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
        )


class TriageWorkflow:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def run(self, request: TriageRunRequest, user: CurrentUser) -> TriageRunResponse:
        service = SupabaseService(self.settings)
        intent = IntentClassifier().classify(request)
        asset = self._load_asset(service, user, request.asset_id)
        rag = RetrievalAgent(self.settings).retrieve(request, user)
        risk = RiskScoringTool().score(request)
        actions, safety_checks, parts_tools = ActionPlanner().plan(rag, risk)
        draft = WorkOrderDraftAgent().draft(asset, risk)
        likely_failure = risk.likely_failure_modes[0] if risk.likely_failure_modes else "unknown failure mode"
        created_work_order_id = self._persist_outputs(service, user, request, risk, draft, rag, intent)
        asset_name = asset.name if asset else "Line 2 spindle"

        return TriageRunResponse(
            issue_summary=(
                f"{asset_name} shows elevated torque, rising tool wear, and vibration. "
                f"Risk model reports {risk.risk_level} risk."
            ),
            urgency=risk.risk_level,
            risk_score=risk.risk_score,
            likely_failure_mode=likely_failure,
            recommended_actions=actions,
            safety_checks=safety_checks,
            parts_tools_needed=parts_tools,
            drafted_work_order=draft,
            citations=rag.citations,
            model_used=f"{rag.model_used}+{risk.model_version}",
            created_work_order_id=created_work_order_id,
        )

    def _load_asset(self, service: SupabaseService, user: CurrentUser, asset_id: str) -> AssetRead | None:
        try:
            return service.get_asset(user, asset_id)
        except SupabaseServiceError:
            return None

    def _persist_outputs(
        self,
        service: SupabaseService,
        user: CurrentUser,
        request: TriageRunRequest,
        risk: RiskPredictResponse,
        draft: DraftedWorkOrder,
        rag: RagAskResponse,
        intent: ClassifiedIntent,
    ) -> str | None:
        created_work_order_id: str | None = None
        try:
            service.create_model_prediction(
                user,
                asset_id=request.asset_id,
                model_version=risk.model_version,
                risk_score=risk.risk_score,
                predicted_label=risk.risk_level,
                features=request.telemetry.model_dump(),
                explanation={"likely_failure_modes": risk.likely_failure_modes, "top_features": risk.top_features},
            )
            if request.create_draft_work_order and intent.requires_work_order:
                order = service.create_work_order(
                    user,
                    asset_id=request.asset_id,
                    title=draft.title,
                    description=draft.description,
                    priority=draft.priority,
                    ai_recommendation={
                        "recommended_actions": rag.next_steps,
                        "citations": [citation.model_dump() for citation in rag.citations],
                    },
                )
                created_work_order_id = order.id
            service.create_audit_log(
                user,
                action="triage.run",
                entity_type="asset",
                entity_id=request.asset_id,
                details={
                    "intent": intent.intent,
                    "risk_score": risk.risk_score,
                    "urgency": risk.risk_level,
                    "citation_count": len(rag.citations),
                    "created_work_order_id": created_work_order_id,
                },
            )
        except SupabaseServiceError:
            if not self.settings.demo_mode:
                raise
        return created_work_order_id

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from urllib import error, parse, request

from app.core.config import Settings, get_settings
from app.schemas.assets import AssetRead
from app.schemas.documents import DocumentRead, RetrievedChunk
from app.schemas.incidents import IncidentRead
from app.schemas.work_orders import WorkOrderRead


class SupabaseServiceError(RuntimeError):
    pass


class SupabaseAuthError(SupabaseServiceError):
    pass


class SupabaseUnavailableError(SupabaseServiceError):
    pass


@dataclass(frozen=True)
class VerifiedSupabaseUser:
    user_id: str
    email: str | None


@dataclass(frozen=True)
class SupabaseProfile:
    profile_id: str
    user_id: str
    organization_id: str
    plant_id: str
    assigned_plant_ids: list[str]
    role: str
    display_name: str
    email: str | None


class SupabaseService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def verify_access_token(self, token: str) -> VerifiedSupabaseUser:
        if not token:
            raise SupabaseAuthError("Empty bearer token")
        if not self.settings.supabase_url or self.settings.supabase_anon_key is None:
            raise SupabaseAuthError("Supabase auth settings are not configured")

        data = self._request_json(
            "GET",
            "/auth/v1/user",
            key="anon",
            bearer_token=token,
        )
        user_id = data.get("id")
        if not isinstance(user_id, str) or not user_id:
            raise SupabaseAuthError("Supabase token did not resolve to a user")
        email = data.get("email")
        return VerifiedSupabaseUser(
            user_id=user_id,
            email=email if isinstance(email, str) else None,
        )

    def load_profile_for_user(self, user_id: str) -> SupabaseProfile:
        rows = self.rest_select(
            "profiles",
            {
                "select": "id,user_id,organization_id,plant_id,assigned_plant_ids,role,display_name,email,is_active",
                "user_id": f"eq.{user_id}",
                "is_active": "eq.true",
                "limit": "1",
            },
        )
        if not rows:
            raise SupabaseAuthError("No active PlantOps profile exists for this user")
        profile = rows[0]
        plant_id = profile.get("plant_id")
        if not isinstance(plant_id, str) or not plant_id:
            raise SupabaseAuthError("Profile is missing an assigned plant")
        role = profile.get("role")
        if not isinstance(role, str):
            raise SupabaseAuthError("Profile is missing a role")
        assigned = profile.get("assigned_plant_ids") or [plant_id]
        if not isinstance(assigned, list):
            assigned = [plant_id]
        return SupabaseProfile(
            profile_id=str(profile["id"]),
            user_id=str(profile["user_id"]),
            organization_id=str(profile["organization_id"]),
            plant_id=plant_id,
            assigned_plant_ids=[str(value) for value in assigned if value],
            role=role,
            display_name=str(profile.get("display_name") or "PlantOps user"),
            email=profile.get("email") if isinstance(profile.get("email"), str) else None,
        )

    def rest_select(self, table: str, query: dict[str, str]) -> list[dict[str, Any]]:
        data = self._request_json("GET", f"/rest/v1/{table}", query=query, key="service")
        if not isinstance(data, list):
            raise SupabaseUnavailableError(f"Supabase REST table {table} returned a non-list payload")
        return [row for row in data if isinstance(row, dict)]

    def rest_insert(self, table: str, payload: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
        data = self._request_json(
            "POST",
            f"/rest/v1/{table}",
            payload=payload,
            key="service",
            prefer="return=representation",
        )
        if not isinstance(data, list):
            raise SupabaseUnavailableError(f"Supabase REST insert into {table} returned a non-list payload")
        return [row for row in data if isinstance(row, dict)]

    def rest_update(
        self,
        table: str,
        query: dict[str, str],
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        data = self._request_json(
            "PATCH",
            f"/rest/v1/{table}",
            query=query,
            payload=payload,
            key="service",
            prefer="return=representation",
        )
        if not isinstance(data, list):
            raise SupabaseUnavailableError(f"Supabase REST update on {table} returned a non-list payload")
        return [row for row in data if isinstance(row, dict)]

    def rpc(self, function_name: str, payload: dict[str, Any]) -> Any:
        return self._request_json(
            "POST",
            f"/rest/v1/rpc/{function_name}",
            payload=payload,
            key="service",
        )

    def list_assets(self, user: Any) -> list[AssetRead]:
        plant_id = self._scoped_plant_id(user, None)
        rows = self.rest_select(
            "assets",
            {
                "select": "id,name,line_name,status,risk_score,plant_id",
                "organization_id": f"eq.{user.organization_id}",
                "plant_id": f"eq.{plant_id}",
                "order": "risk_score.desc",
            },
        )
        return [
            AssetRead(
                id=str(row["id"]),
                name=str(row["name"]),
                line=str(row.get("line_name") or "Unknown line"),
                status=self._api_asset_status(str(row.get("status") or "watch")),
                risk_score=float(row.get("risk_score") or 0),
                plant_id=str(row["plant_id"]),
            )
            for row in rows
        ]

    def list_incidents(self, user: Any) -> list[IncidentRead]:
        plant_id = self._scoped_plant_id(user, None)
        rows = self.rest_select(
            "incidents",
            {
                "select": "id,asset_id,title,severity,status,observed_at,plant_id",
                "organization_id": f"eq.{user.organization_id}",
                "plant_id": f"eq.{plant_id}",
                "order": "observed_at.desc",
            },
        )
        return [
            IncidentRead(
                id=str(row["id"]),
                asset_id=str(row["asset_id"]),
                title=str(row["title"]),
                severity=str(row["severity"]),
                status=str(row["status"]),
                reported_at=str(row.get("observed_at") or ""),
            )
            for row in rows
        ]

    def list_documents(self, user: Any) -> list[DocumentRead]:
        plant_id = self._scoped_plant_id(user, None)
        rows = self.rest_select(
            "documents",
            {
                "select": "id,title,document_type,plant_id,source_uri",
                "organization_id": f"eq.{user.organization_id}",
                "plant_id": f"eq.{plant_id}",
                "order": "created_at.desc",
            },
        )
        return [
            DocumentRead(
                id=str(row["id"]),
                title=str(row["title"]),
                document_type=str(row["document_type"]),
                plant_id=str(row["plant_id"]),
                source_uri=row.get("source_uri") if isinstance(row.get("source_uri"), str) else None,
            )
            for row in rows
        ]

    def list_document_chunks(self, user: Any, *, plant_id: str | None = None) -> list[RetrievedChunk]:
        scoped_plant_id = self._scoped_plant_id(user, plant_id)
        rows = self.rest_select(
            "document_chunks",
            {
                "select": "id,document_id,title,content,source_uri,source_page,page_number,plant_id",
                "organization_id": f"eq.{user.organization_id}",
                "plant_id": f"eq.{scoped_plant_id}",
                "order": "document_id.asc,chunk_index.asc",
            },
        )
        return [self._chunk_from_row(row) for row in rows]

    def create_document(
        self,
        user: Any,
        *,
        title: str,
        document_type: str,
        source_uri: str | None,
        plant_id: str | None = None,
    ) -> DocumentRead:
        scoped_plant_id = self._scoped_plant_id(user, plant_id)
        rows = self.rest_insert(
            "documents",
            {
                "organization_id": user.organization_id,
                "plant_id": scoped_plant_id,
                "created_by": user.profile_id,
                "title": title,
                "document_type": document_type,
                "source_uri": source_uri,
            },
        )
        row = rows[0]
        return DocumentRead(
            id=str(row["id"]),
            title=str(row["title"]),
            document_type=str(row["document_type"]),
            plant_id=str(row["plant_id"]),
            source_uri=row.get("source_uri") if isinstance(row.get("source_uri"), str) else None,
        )

    def create_document_chunks(
        self,
        user: Any,
        *,
        document_id: str,
        title: str,
        chunks: list[dict[str, Any]],
        plant_id: str | None = None,
    ) -> list[RetrievedChunk]:
        scoped_plant_id = self._scoped_plant_id(user, plant_id)
        payload = []
        for chunk in chunks:
            payload.append(
                {
                    "organization_id": user.organization_id,
                    "plant_id": scoped_plant_id,
                    "document_id": document_id,
                    "created_by": user.profile_id,
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "citation_label": chunk["citation_label"],
                    "page_number": chunk.get("source_page"),
                    "title": title,
                    "source_uri": chunk.get("source_uri"),
                    "source_page": chunk.get("source_page"),
                    "embedding": self._vector_literal(chunk["embedding"]) if chunk.get("embedding") else None,
                    "metadata": chunk.get("metadata") or {},
                }
            )
        rows = self.rest_insert("document_chunks", payload)
        return [self._chunk_from_row(row) for row in rows]

    def match_document_chunks(
        self,
        user: Any,
        *,
        query_embedding: list[float],
        plant_id: str | None,
        top_k: int,
    ) -> list[RetrievedChunk]:
        scoped_plant_id = self._scoped_plant_id(user, plant_id)
        data = self.rpc(
            "match_document_chunks",
            {
                "query_embedding": self._vector_literal(query_embedding),
                "match_count": top_k,
                "filter_organization_id": user.organization_id,
                "filter_plant_id": scoped_plant_id,
            },
        )
        if not isinstance(data, list):
            raise SupabaseUnavailableError("match_document_chunks returned a non-list payload")
        return [
            RetrievedChunk(
                chunk_id=str(row["chunk_id"]),
                document_id=str(row["document_id"]),
                title=str(row["title"]),
                content=str(row["content"]),
                source_uri=str(row.get("source_uri") or "supabase://document-chunk"),
                source_page=row.get("source_page") if isinstance(row.get("source_page"), int) else None,
                score=float(row.get("similarity") or 0),
            )
            for row in data
            if isinstance(row, dict)
        ]

    def create_rag_query(
        self,
        user: Any,
        *,
        query: str,
        answer: str,
        citations: list[dict[str, Any]],
        model_used: str,
        fallback_used: bool,
        latency_ms: int | None,
        plant_id: str | None = None,
    ) -> None:
        scoped_plant_id = self._scoped_plant_id(user, plant_id)
        self.rest_insert(
            "rag_queries",
            {
                "organization_id": user.organization_id,
                "plant_id": scoped_plant_id,
                "created_by": user.profile_id,
                "query": query,
                "answer": answer,
                "citations": citations,
                "model_used": model_used,
                "fallback_used": fallback_used,
                "latency_ms": latency_ms,
            },
        )

    def create_work_order(
        self,
        user: Any,
        *,
        asset_id: str,
        title: str,
        description: str,
        priority: str,
        status: str = "draft",
        ai_recommendation: dict[str, Any] | None = None,
        plant_id: str | None = None,
    ) -> WorkOrderRead:
        scoped_plant_id = self._scoped_plant_id(user, plant_id)
        rows = self.rest_insert(
            "work_orders",
            {
                "organization_id": user.organization_id,
                "plant_id": scoped_plant_id,
                "asset_id": asset_id,
                "created_by": user.profile_id,
                "title": title,
                "description": description,
                "priority": priority,
                "status": status,
                "ai_recommendation": ai_recommendation or {},
            },
        )
        return self._work_order_from_row(rows[0])

    def list_work_orders(self, user: Any) -> list[WorkOrderRead]:
        rows = self.rest_select(
            "work_orders",
            {
                "select": "id,asset_id,title,status,priority,description,ai_recommendation,created_at,plant_id",
                "organization_id": f"eq.{user.organization_id}",
                "plant_id": f"eq.{self._scoped_plant_id(user, None)}",
                "order": "created_at.desc",
            },
        )
        return [self._work_order_from_row(row) for row in rows]

    def update_work_order(
        self,
        user: Any,
        *,
        order_id: str,
        status: str,
        note: str,
    ) -> WorkOrderRead:
        rows = self.rest_update(
            "work_orders",
            {
                "id": f"eq.{order_id}",
                "organization_id": f"eq.{user.organization_id}",
                "plant_id": f"eq.{self._scoped_plant_id(user, None)}",
            },
            {
                "status": status,
                "reviewed_by": user.profile_id,
                "ai_recommendation": {"transition_note": note},
            },
        )
        if not rows:
            raise SupabaseUnavailableError("Work order was not found or not in user scope")
        return self._work_order_from_row(rows[0])

    def create_audit_log(
        self,
        user: Any,
        *,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        details: dict[str, Any] | None = None,
        plant_id: str | None = None,
    ) -> None:
        self.rest_insert(
            "audit_logs",
            {
                "organization_id": user.organization_id,
                "plant_id": self._scoped_plant_id(user, plant_id),
                "created_by": user.profile_id,
                "actor_user_id": user.user_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details or {},
            },
        )

    def create_model_prediction(
        self,
        user: Any,
        *,
        asset_id: str,
        model_version: str,
        risk_score: float,
        predicted_label: str,
        features: dict[str, Any],
        explanation: dict[str, Any],
        plant_id: str | None = None,
    ) -> None:
        self.rest_insert(
            "model_predictions",
            {
                "organization_id": user.organization_id,
                "plant_id": self._scoped_plant_id(user, plant_id),
                "asset_id": asset_id,
                "created_by": user.profile_id,
                "model_name": "ai4i-failure-risk",
                "model_version": model_version,
                "risk_score": risk_score,
                "predicted_label": predicted_label,
                "features": features,
                "explanation": explanation,
            },
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str] | None = None,
        payload: Any | None = None,
        key: str,
        bearer_token: str | None = None,
        prefer: str | None = None,
    ) -> Any:
        if not self.settings.supabase_url:
            raise SupabaseUnavailableError("SUPABASE_URL is not configured")
        api_key = self._api_key(key)
        encoded_query = f"?{parse.urlencode(query or {}, safe='(),.*')}" if query else ""
        url = f"{self.settings.supabase_url.rstrip('/')}{path}{encoded_query}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {bearer_token or api_key}",
            "Accept": "application/json",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if prefer:
            headers["Prefer"] = prefer

        http_request = request.Request(url, data=body, method=method, headers=headers)
        try:
            with request.urlopen(http_request, timeout=15) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return None
                return json.loads(raw)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            if exc.code in {401, 403}:
                raise SupabaseAuthError("Supabase rejected the authenticated request") from exc
            raise SupabaseUnavailableError(f"Supabase HTTP {exc.code}: {detail}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise SupabaseUnavailableError(f"Supabase request failed: {exc.__class__.__name__}") from exc

    def _api_key(self, key: str) -> str:
        if key == "anon":
            if self.settings.supabase_anon_key is None:
                raise SupabaseUnavailableError("SUPABASE_ANON_KEY is not configured")
            return self.settings.supabase_anon_key.get_secret_value()
        if self.settings.supabase_service_role_key is None:
            raise SupabaseUnavailableError("SUPABASE_SERVICE_ROLE_KEY is not configured")
        return self.settings.supabase_service_role_key.get_secret_value()

    def _scoped_plant_id(self, user: Any, plant_id: str | None) -> str:
        scoped = plant_id or user.plant_id
        allowed = set(getattr(user, "assigned_plant_ids", []) or [user.plant_id])
        if scoped != user.plant_id and scoped not in allowed:
            raise SupabaseAuthError("Requested plant is outside the authenticated user's scope")
        return scoped

    def _api_asset_status(self, status: str) -> str:
        return {
            "healthy": "healthy",
            "watch": "watch",
            "high_risk": "high_risk",
            "degraded": "high_risk",
            "critical": "critical",
            "offline": "critical",
        }.get(status, "watch")

    def _chunk_from_row(self, row: dict[str, Any]) -> RetrievedChunk:
        return RetrievedChunk(
            chunk_id=str(row["id"]),
            document_id=str(row["document_id"]),
            title=str(row.get("title") or "Untitled evidence"),
            content=str(row["content"]),
            source_uri=str(row.get("source_uri") or "supabase://document-chunk"),
            source_page=(
                row.get("source_page")
                if isinstance(row.get("source_page"), int)
                else row.get("page_number") if isinstance(row.get("page_number"), int) else None
            ),
            score=float(row["score"]) if isinstance(row.get("score"), int | float) else None,
        )

    def _work_order_from_row(self, row: dict[str, Any]) -> WorkOrderRead:
        recommendation = row.get("ai_recommendation") if isinstance(row.get("ai_recommendation"), dict) else {}
        return WorkOrderRead(
            id=str(row["id"]),
            asset_id=str(row["asset_id"]),
            title=str(row["title"]),
            status=str(row["status"]),
            priority=str(row["priority"]),
            assigned_role=str(recommendation.get("assigned_role") or "reliability_engineer"),
            description=row.get("description") if isinstance(row.get("description"), str) else None,
            audit_events=[
                f"created:{row.get('created_at') or 'unknown'}",
                f"status:{row.get('status')}",
            ],
        )

    def _vector_literal(self, embedding: list[float]) -> str:
        return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"

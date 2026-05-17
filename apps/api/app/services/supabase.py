from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from urllib import error, parse, request

from app.core.config import Settings, get_settings


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

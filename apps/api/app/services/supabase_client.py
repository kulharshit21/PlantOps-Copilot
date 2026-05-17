from dataclasses import dataclass
from urllib import error, request

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class SupabaseHealth:
    configured: bool
    reachable: bool
    project_url: str | None
    detail: str


class SupabaseClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def health(self) -> SupabaseHealth:
        if not self.settings.supabase_url or self.settings.supabase_service_role_key is None:
            return SupabaseHealth(
                configured=False,
                reachable=False,
                project_url=self.settings.supabase_url,
                detail="SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required on the backend.",
            )

        url = f"{self.settings.supabase_url.rstrip('/')}/rest/v1/"
        http_request = request.Request(
            url,
            method="GET",
            headers={
                "apikey": self.settings.supabase_service_role_key.get_secret_value(),
                "Authorization": f"Bearer {self.settings.supabase_service_role_key.get_secret_value()}",
            },
        )
        try:
            with request.urlopen(http_request, timeout=5) as response:
                return SupabaseHealth(
                    configured=True,
                    reachable=200 <= response.status < 500,
                    project_url=self.settings.supabase_url,
                    detail=f"Supabase REST responded with HTTP {response.status}.",
                )
        except error.HTTPError as exc:
            return SupabaseHealth(
                configured=True,
                reachable=exc.code in {200, 401, 403, 404},
                project_url=self.settings.supabase_url,
                detail=f"Supabase REST responded with HTTP {exc.code}.",
            )
        except OSError as exc:
            return SupabaseHealth(
                configured=True,
                reachable=False,
                project_url=self.settings.supabase_url,
                detail=f"Supabase REST unreachable: {exc.__class__.__name__}.",
            )

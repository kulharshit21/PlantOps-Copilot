from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from time import perf_counter

from app.api.routes import assets, documents, incidents, ops, rag, risk, system, triage, work_orders
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.services.metrics import METRICS

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    active_settings = settings or get_settings()
    active_settings.validate_startup_security()
    if active_settings.demo_mode:
        logger.warning("DEMO MODE ACTIVE: unauthenticated local demo requests are allowed.")

    app = FastAPI(
        title=active_settings.app_name,
        version=active_settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        started = perf_counter()
        is_error = False
        try:
            response = await call_next(request)
            is_error = response.status_code >= 500
            return response
        except Exception:
            is_error = True
            raise
        finally:
            METRICS.record_request(
                latency_ms=(perf_counter() - started) * 1000,
                is_error=is_error,
            )

    # TODO(rate-limit): add per-user/IP limiter before external LLM and write routes.
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "bad_request",
                "detail": str(exc),
                "request_id": request.headers.get("X-Request-ID"),
            },
        )

    app.include_router(system.router)
    app.include_router(assets.router)
    app.include_router(incidents.router)
    app.include_router(documents.router)
    app.include_router(rag.router)
    app.include_router(risk.router)
    app.include_router(triage.router)
    app.include_router(work_orders.router)
    app.include_router(ops.router)

    return app


app = create_app()

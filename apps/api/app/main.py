from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import assets, documents, incidents, ops, rag, risk, system, work_orders
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    active_settings = settings or get_settings()
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
    app.include_router(work_orders.router)
    app.include_router(ops.router)

    return app


app = create_app()

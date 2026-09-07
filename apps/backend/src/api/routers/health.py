"""Health check endpoints for container liveness and DB readiness."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.dependencies import get_db_session, get_settings
from api.schemas.health import HealthResponse
from core.settings import Settings

router = APIRouter(tags=["Health"])


@router.get("/healthz", response_model=HealthResponse, summary="Liveness check")
def healthz(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Basic liveness probe indicating the HTTP process is running."""
    return HealthResponse(
        status="healthy",
        database="unknown",
        version=settings.api_version,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/api/v1/health", response_model=HealthResponse, summary="Readiness check")
def health(
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> HealthResponse | JSONResponse:
    """Readiness probe checking database connectivity."""
    now = datetime.now(timezone.utc)
    try:
        db.execute(text("SELECT 1"))
        return HealthResponse(
            status="healthy",
            database="connected",
            version=settings.api_version,
            timestamp=now,
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": "disconnected",
                "version": settings.api_version,
                "timestamp": now.isoformat(),
                "detail": str(exc),
            },
        )

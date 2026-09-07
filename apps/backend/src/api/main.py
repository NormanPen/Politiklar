"""FastAPI application factory and route registration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.dependencies import get_settings
from api.routers import (
    health_router,
    members_router,
    sources_router,
    speeches_router,
    votes_router,
)
from core.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Creates and configures the Politiklar FastAPI application."""
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="Civic-tech transparency platform for official German parliamentary data.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    origins = settings.cors_origins_list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router)
    app.include_router(members_router)
    app.include_router(votes_router)
    app.include_router(speeches_router)
    app.include_router(sources_router)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()

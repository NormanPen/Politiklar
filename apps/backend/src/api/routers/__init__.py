"""API router endpoints."""

from .health import router as health_router
from .members import router as members_router
from .sources import router as sources_router
from .speeches import router as speeches_router
from .votes import router as votes_router

__all__ = [
    "health_router",
    "members_router",
    "sources_router",
    "speeches_router",
    "votes_router",
]

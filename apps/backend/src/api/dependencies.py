"""FastAPI dependencies for settings and database sessions."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy.orm import Session, sessionmaker

from core.settings import Settings
from db.relational.session import create_session_factory


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    settings = get_settings()
    return create_session_factory(settings)


def get_db_session() -> Generator[Session, None, None]:
    """Yields a database session and guarantees clean closure and rollback on errors."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

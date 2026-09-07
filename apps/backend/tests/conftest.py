"""Common pytest fixtures for backend tests."""

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.dependencies import get_db_session
from api.main import create_app
from db.relational.base import Base


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provides a fresh isolated in-memory SQLite database session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def api_app(db_session: Session) -> FastAPI:
    """Provides a test FastAPI instance with database session overridden."""
    app = create_app()

    def override_get_db_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    return app


@pytest.fixture(scope="function")
def client(api_app: FastAPI) -> Generator[TestClient, None, None]:
    """Provides an HTTP test client."""
    with TestClient(api_app) as c:
        yield c

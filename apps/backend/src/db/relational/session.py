"""Database engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.settings import Settings


def create_session_factory(settings: Settings) -> sessionmaker:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)
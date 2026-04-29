from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_app_settings


def _build_database_url() -> str:
    database_url = (get_app_settings().database_url or "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to initialize SQLAlchemy.")
    return database_url


engine = create_engine(_build_database_url(), pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()

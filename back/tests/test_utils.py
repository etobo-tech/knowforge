import pytest

from utils import get_database_url, get_pgvector_connection_strings


def test_get_database_url_returns_configured_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    assert get_database_url() == "sqlite:///:memory:"


def test_get_database_url_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        get_database_url()


def test_get_pgvector_connection_strings_from_supabase_style_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:secret@db.example.com:5432/postgres",
    )
    sync_url, async_url = get_pgvector_connection_strings()
    assert sync_url == "postgresql+psycopg2://user:secret@db.example.com:5432/postgres"
    assert async_url == "postgresql+asyncpg://user:secret@db.example.com:5432/postgres"


def test_get_pgvector_connection_strings_rejects_sqlite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    with pytest.raises(ValueError, match="PostgreSQL"):
        get_pgvector_connection_strings()

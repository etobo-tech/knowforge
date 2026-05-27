import os

from sqlalchemy.engine.url import make_url


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set")
    return database_url


def get_pgvector_connection_strings() -> tuple[str, str]:
    url = make_url(get_database_url())
    if url.drivername.split("+")[0] not in ("postgresql", "postgres"):
        raise ValueError(
            f"PGVectorStore requires PostgreSQL; got DATABASE_URL driver {url.drivername!r}"
        )
    sync = url.set(drivername="postgresql+psycopg2")
    async_ = url.set(drivername="postgresql+asyncpg")
    return (
        sync.render_as_string(hide_password=False),
        async_.render_as_string(hide_password=False),
    )

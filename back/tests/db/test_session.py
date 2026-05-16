from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session, sessionmaker

from db.session import get_db


def test_get_db_yields_and_closes_session(
    engine: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_session_factory = sessionmaker(bind=engine)
    monkeypatch.setattr("db.session.SessionLocal", test_session_factory)

    generator: Generator[Session, None, None] = get_db()
    session = next(generator)

    assert isinstance(session, Session)

    generator.close()

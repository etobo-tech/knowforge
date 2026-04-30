import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.db import session as db_session


class TestDbSession(unittest.TestCase):
    def test_build_database_url_raises_when_missing(self) -> None:
        settings = SimpleNamespace(database_url=" ")
        with patch("app.db.session.get_app_settings", return_value=settings):
            with self.assertRaises(RuntimeError):
                db_session._build_database_url()

    def test_get_db_session_yields_and_closes_session(self) -> None:
        fake_session = Mock()
        with patch.object(db_session, "SessionFactory", return_value=fake_session):
            session_gen = db_session.get_db_session()
            yielded_session = next(session_gen)
            self.assertIs(yielded_session, fake_session)
            with self.assertRaises(StopIteration):
                next(session_gen)

        fake_session.close.assert_called_once()

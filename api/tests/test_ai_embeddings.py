import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.ai_embeddings import build_openai_embedding_client


class TestAiEmbeddings(unittest.TestCase):
    def test_raises_when_openai_api_key_missing(self) -> None:
        settings = SimpleNamespace(openai_api_key="  ", embedding_model="text-embedding-3-small")
        with patch("app.services.ai_embeddings.get_app_settings", return_value=settings):
            with self.assertRaises(RuntimeError):
                build_openai_embedding_client()

    def test_builds_embedding_client_with_settings_values(self) -> None:
        settings = SimpleNamespace(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
        )
        with patch("app.services.ai_embeddings.get_app_settings", return_value=settings):
            with patch("app.services.ai_embeddings.OpenAIEmbedding") as embedding_cls:
                client = build_openai_embedding_client()

        embedding_cls.assert_called_once_with(
            model="text-embedding-3-small",
            api_key="test-key",
        )
        self.assertEqual(client, embedding_cls.return_value)

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.schemas.chat import ChatRequest
from app.services.rag_chat_service import answer_question


class TestRagChatService(unittest.TestCase):
    @patch("app.services.rag_chat_service.generate_grounded_answer")
    @patch("app.services.rag_chat_service.build_openai_embedding_client")
    @patch("app.services.rag_chat_service.RagRepository")
    @patch("app.services.rag_chat_service.SessionFactory")
    def test_answer_question_returns_grounded_response_with_citations(
        self,
        mock_session_factory,
        mock_repository_class,
        mock_embedding_builder,
        mock_generate_answer,
    ) -> None:
        session = MagicMock()
        mock_session_factory.return_value.__enter__.return_value = session

        repository = MagicMock()
        chunk = SimpleNamespace(
            id=uuid4(),
            document_id=uuid4(),
            content="This is relevant context.",
        )
        repository.search_similar_chunks.return_value = [(chunk, 0.95)]
        mock_repository_class.return_value = repository

        embedding_client = MagicMock()
        embedding_client.get_text_embedding.return_value = [0.1, 0.2, 0.3]
        mock_embedding_builder.return_value = embedding_client

        mock_generate_answer.return_value = "Grounded answer."

        response = answer_question(
            request=ChatRequest(workspace_id="ws-1", question="What is this about?")
        )

        self.assertEqual(response.answer, "Grounded answer.")
        self.assertEqual(len(response.citations), 1)
        self.assertEqual(response.citations[0].file_id, str(chunk.document_id))
        self.assertEqual(response.citations[0].chunk_id, str(chunk.id))
        repository.log_metric_event.assert_called_once()
        session.commit.assert_called_once()

    @patch("app.services.rag_chat_service.build_openai_embedding_client")
    @patch("app.services.rag_chat_service.RagRepository")
    @patch("app.services.rag_chat_service.SessionFactory")
    def test_answer_question_returns_fallback_without_relevant_context(
        self,
        mock_session_factory,
        mock_repository_class,
        mock_embedding_builder,
    ) -> None:
        session = MagicMock()
        mock_session_factory.return_value.__enter__.return_value = session

        repository = MagicMock()
        weak_chunk = SimpleNamespace(
            id=uuid4(),
            document_id=uuid4(),
            content="Weak match.",
        )
        repository.search_similar_chunks.return_value = [(weak_chunk, 0.01)]
        mock_repository_class.return_value = repository

        embedding_client = MagicMock()
        embedding_client.get_text_embedding.return_value = [0.9, 0.8, 0.7]
        mock_embedding_builder.return_value = embedding_client

        response = answer_question(
            request=ChatRequest(workspace_id="ws-1", question="Out-of-context question?")
        )

        self.assertEqual(
            response.answer,
            "I do not have enough context in the uploaded files to answer that question.",
        )
        self.assertEqual(response.citations, [])
        repository.log_metric_event.assert_not_called()
        session.commit.assert_not_called()

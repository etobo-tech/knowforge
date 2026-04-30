import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.types.enums import FileStatus
from app.services.rag_ingestion import persist_rag_document


class TestRagIngestion(unittest.TestCase):
    @patch("app.services.rag_ingestion._persist_ingestion_success")
    @patch("app.services.rag_ingestion.RagRepository")
    @patch("app.services.rag_ingestion.SessionFactory")
    def test_persist_rag_document_returns_ready_on_success(
        self,
        mock_session_factory,
        mock_repository_class,
        mock_persist_success,
    ) -> None:
        session = MagicMock()
        mock_session_factory.return_value.__enter__.return_value = session
        mock_repository = MagicMock()
        mock_repository_class.return_value = mock_repository

        result = persist_rag_document(
            workspace_id="ws-1",
            file_id=str(uuid4()),
            filename="notes.md",
            storage_path="data/uploads/ws-1/notes.md",
            chunks=["chunk-1", "chunk-2"],
        )

        self.assertEqual(result, FileStatus.READY)
        session.commit.assert_called_once()
        session.rollback.assert_not_called()
        mock_persist_success.assert_called_once()

    @patch("app.services.rag_ingestion._persist_ingestion_success")
    @patch("app.services.rag_ingestion.RagRepository")
    @patch("app.services.rag_ingestion.SessionFactory")
    def test_persist_rag_document_returns_failed_on_exception(
        self,
        mock_session_factory,
        mock_repository_class,
        mock_persist_success,
    ) -> None:
        session = MagicMock()
        mock_session_factory.return_value.__enter__.return_value = session
        mock_repository = MagicMock()
        mock_repository_class.return_value = mock_repository
        mock_persist_success.side_effect = RuntimeError("boom")

        result = persist_rag_document(
            workspace_id="ws-1",
            file_id=str(uuid4()),
            filename="notes.md",
            storage_path="data/uploads/ws-1/notes.md",
            chunks=["chunk-1"],
        )

        self.assertEqual(result, FileStatus.FAILED)
        session.rollback.assert_called_once()
        session.commit.assert_not_called()

    def test_persist_rag_document_returns_failed_with_empty_chunks(self) -> None:
        result = persist_rag_document(
            workspace_id="ws-1",
            file_id=str(uuid4()),
            filename="notes.md",
            storage_path="data/uploads/ws-1/notes.md",
            chunks=[],
        )

        self.assertEqual(result, FileStatus.FAILED)

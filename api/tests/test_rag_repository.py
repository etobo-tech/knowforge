import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from app.db.models.rag import ChunkModel, DocumentStatus, MetricEventType
from app.services.repositories.rag_repository import RagRepository


class TestRagRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.session = MagicMock()
        self.repository = RagRepository(session=self.session)

    def test_create_document_adds_and_flushes(self) -> None:
        document_id = uuid4()

        document = self.repository.create_document(
            document_id=document_id,
            workspace_id="ws-1",
            filename="notes.md",
            storage_path="data/uploads/ws-1/notes.md",
            status=DocumentStatus.PROCESSING,
        )

        self.assertEqual(document.id, document_id)
        self.assertEqual(document.workspace_id, "ws-1")
        self.assertEqual(document.filename, "notes.md")
        self.assertEqual(document.status, DocumentStatus.PROCESSING)
        self.session.add.assert_called_once()
        self.session.flush.assert_called_once()

    def test_set_document_status_updates_via_query_chain(self) -> None:
        document_id = uuid4()
        query = self.session.query.return_value
        filtered = query.filter.return_value
        filtered.update.return_value = 1

        updated = self.repository.set_document_status(
            document_id=document_id,
            status=DocumentStatus.READY,
        )

        self.assertEqual(updated, 1)
        self.session.query.assert_called_once()
        query.filter.assert_called_once()
        filtered.update.assert_called_once_with({"status": DocumentStatus.READY})

    def test_add_chunks_adds_all_only_when_non_empty(self) -> None:
        self.repository.add_chunks(chunks=[])
        self.session.add_all.assert_not_called()

        chunk = ChunkModel(
            document_id=uuid4(),
            workspace_id="ws-1",
            chunk_index=0,
            content="chunk",
            embedding=[0.1] * 1536,
        )
        self.repository.add_chunks(chunks=[chunk])
        self.session.add_all.assert_called_once()

    def test_log_metric_event_adds_and_flushes(self) -> None:
        file_id = uuid4()
        event = self.repository.log_metric_event(
            workspace_id="ws-1",
            event_type=MetricEventType.FILE_UPLOADED,
            file_id=file_id,
            duration_ms=120,
            payload={"source": "test"},
        )

        self.assertEqual(event.workspace_id, "ws-1")
        self.assertEqual(event.event_type, MetricEventType.FILE_UPLOADED)
        self.assertEqual(event.file_id, file_id)
        self.assertEqual(event.duration_ms, 120)
        self.assertEqual(event.payload, {"source": "test"})
        self.session.add.assert_called()
        self.session.flush.assert_called()

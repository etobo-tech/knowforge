from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.rag import ChunkModel, DocumentModel, DocumentStatus, MetricEventModel, MetricEventType


class RagRepository:
    def __init__(self, *, session: Session):
        self._session = session

    def create_document(
        self,
        *,
        document_id: UUID | None = None,
        workspace_id: str,
        filename: str,
        storage_path: str,
        status: DocumentStatus,
    ) -> DocumentModel:
        document = DocumentModel(
            id=document_id,
            workspace_id=workspace_id,
            filename=filename,
            storage_path=storage_path,
            status=status,
        )
        self._session.add(document)
        self._session.flush()
        return document

    def set_document_status(self, *, document_id: UUID, status: DocumentStatus) -> int:
        return (
            self._session.query(DocumentModel)
            .filter(DocumentModel.id == document_id)
            .update({"status": status})
        )

    def add_chunks(self, *, chunks: list[ChunkModel]) -> None:
        if chunks:
            self._session.add_all(chunks)

    def search_similar_chunks(
        self, *, workspace_id: str, query_embedding: list[float], top_k: int
    ) -> list[tuple[ChunkModel, float]]:
        distance = ChunkModel.embedding.cosine_distance(query_embedding)
        rows = (
            self._session.query(ChunkModel, (1 - distance).label("score"))
            .filter(ChunkModel.workspace_id == workspace_id)
            .order_by(distance.asc())
            .limit(max(1, top_k))
            .all()
        )
        return [(chunk, float(score)) for chunk, score in rows]

    def log_metric_event(
        self,
        *,
        workspace_id: str,
        event_type: MetricEventType,
        file_id: UUID | None = None,
        duration_ms: int | None = None,
        payload: dict | None = None,
    ) -> MetricEventModel:
        event = MetricEventModel(
            workspace_id=workspace_id,
            event_type=event_type,
            file_id=file_id,
            duration_ms=duration_ms,
            payload=payload or {},
        )
        self._session.add(event)
        self._session.flush()
        return event

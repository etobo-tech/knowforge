from time import perf_counter
from uuid import UUID

from app.db.models.rag import ChunkModel, DocumentStatus, MetricEventType
from app.db.session import SessionFactory
from app.services.ai_embeddings import build_openai_embedding_client
from app.services.repositories.rag_repository import RagRepository
from app.types.enums import FileStatus


def _build_chunk_models(
    *,
    document_uuid: UUID,
    workspace_id: str,
    chunks: list[str],
) -> list[ChunkModel]:
    embedding_client = build_openai_embedding_client()
    return [
        ChunkModel(
            document_id=document_uuid,
            workspace_id=workspace_id,
            chunk_index=index,
            content=chunk,
            embedding=embedding_client.get_text_embedding(chunk),
        )
        for index, chunk in enumerate(chunks)
    ]


def _persist_ingestion_success(
    *,
    repository: RagRepository,
    workspace_id: str,
    document_uuid: UUID,
    filename: str,
    storage_path: str,
    chunks: list[str],
    started: float,
) -> None:
    repository.create_document(
        document_id=document_uuid,
        workspace_id=workspace_id,
        filename=filename,
        storage_path=storage_path,
        status=DocumentStatus.PROCESSING,
    )
    repository.log_metric_event(
        workspace_id=workspace_id,
        event_type=MetricEventType.FILE_UPLOADED,
        file_id=document_uuid,
    )
    repository.add_chunks(
        chunks=_build_chunk_models(
            document_uuid=document_uuid,
            workspace_id=workspace_id,
            chunks=chunks,
        )
    )
    repository.set_document_status(
        document_id=document_uuid,
        status=DocumentStatus.READY,
    )
    repository.log_metric_event(
        workspace_id=workspace_id,
        event_type=MetricEventType.FILE_READY,
        file_id=document_uuid,
        duration_ms=int((perf_counter() - started) * 1000),
    )


def persist_rag_document(
    *,
    workspace_id: str,
    file_id: str,
    filename: str,
    storage_path: str,
    chunks: list[str],
) -> FileStatus:
    if not chunks:
        return FileStatus.FAILED

    started = perf_counter()
    document_uuid = UUID(file_id)

    with SessionFactory() as session:
        repository = RagRepository(session=session)
        try:
            _persist_ingestion_success(
                repository=repository,
                workspace_id=workspace_id,
                document_uuid=document_uuid,
                filename=filename,
                storage_path=storage_path,
                chunks=chunks,
                started=started,
            )
            session.commit()
            return FileStatus.READY
        except Exception:
            session.rollback()
            return FileStatus.FAILED

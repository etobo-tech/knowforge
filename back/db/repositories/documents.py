import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Document, DocumentChunk, DocumentStatus

logger = logging.getLogger(__name__)


def db_find_by_user_and_content_hash(
    db: Session, user_id: UUID, content_hash: str
) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id, Document.content_hash == content_hash)
        .first()
    )


def db_persist_new_document(db: Session, document: Document) -> None:
    db.add(document)
    db.flush()


def db_mark_uploaded(db: Session, document: Document) -> Document:
    document.status = DocumentStatus.UPLOADED
    document.error_message = None
    db.commit()
    db.refresh(document)
    return document


def db_begin_indexing(db: Session, document: Document) -> None:
    document.status = DocumentStatus.PROCESSING
    document.error_message = None
    db.flush()


def db_save_indexed_chunks(
    db: Session, document: Document, chunk_texts: list[str]
) -> Document:
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    for index, content in enumerate(chunk_texts):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
                embedding=None,
            )
        )

    document.chunks_count = len(chunk_texts)
    document.status = DocumentStatus.INDEXED
    document.indexed_at = datetime.now(timezone.utc)
    document.error_message = None
    db.commit()
    db.refresh(document)
    return document


def db_mark_indexing_failed(db: Session, document: Document, message: str) -> Document:
    document.status = DocumentStatus.FAILED
    document.error_message = message[:2000]
    db.commit()
    db.refresh(document)
    return document


def db_user_has_indexed_chunks(db: Session, user_id: UUID) -> bool:
    found = db.execute(
        select(Document.id)
        .where(
            Document.user_id == user_id,
            Document.status == DocumentStatus.INDEXED,
            Document.chunks_count > 0,
        )
        .limit(1)
    ).first()
    return found is not None


def db_list_documents_for_user(db: Session, user_id: UUID) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def db_get_document_for_user(
    db: Session, user_id: UUID, document_id: UUID
) -> Document | None:
    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )


def db_delete_document(db: Session, document: Document) -> None:
    from rag.vector_store import delete_document_vectors

    document_id = document.id
    db.delete(document)
    db.commit()

    try:
        delete_document_vectors(document_id)
    except Exception:
        logger.exception(
            "Failed to delete vectors for document %s after DB delete", document_id
        )

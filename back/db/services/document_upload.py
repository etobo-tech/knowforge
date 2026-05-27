import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.factories.documents import build_document
from db.models import Document, DocumentStatus
from db.repositories.documents import db_mark_uploaded, db_persist_new_document
from rag.indexing.errors import public_indexing_error_message
from rag.indexing.pipeline import index_document
from rag.s3 import upload_document_to_s3


def _index_or_raise(db: Session, document: Document, content: bytes) -> None:
    if index_document(db, document, content):
        return
    raise ValueError(public_indexing_error_message(document.error_message))


def handle_existing_document(
    db: Session, existing_document: Document, content: bytes
) -> tuple[Document, bool]:
    if existing_document.status in (DocumentStatus.UPLOADING, DocumentStatus.FAILED):
        try:
            upload_document_to_s3(existing_document, content)
        except Exception:
            db.rollback()
            raise

        db_mark_uploaded(db, existing_document)

    if existing_document.status != DocumentStatus.INDEXED:
        _index_or_raise(db, existing_document, content)

    return existing_document, False


def handle_new_document(
    db: Session,
    file: UploadFile,
    user_id: uuid.UUID,
    content_hash: str,
    size: int,
    content: bytes,
) -> tuple[Document, bool]:
    document = build_document(
        user_id=user_id,
        filename=file.filename or "unnamed",
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        content_hash=content_hash,
    )

    db_persist_new_document(db, document)

    try:
        upload_document_to_s3(document, content)
    except Exception:
        db.rollback()
        raise

    db_mark_uploaded(db, document)
    _index_or_raise(db, document, content)

    return document, True

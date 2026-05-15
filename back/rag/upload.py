import hashlib
import uuid


from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.models import Document, DocumentStatus
from rag.config import Config
from rag.s3 import upload_document_to_s3


def _check_content_type(content_type: str) -> None:
    if content_type not in Config.ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported file type: {content_type}. "
            f"Allowed: {', '.join(sorted(Config.ALLOWED_MIME_TYPES))}"
        )


def _check_file_size(size: int) -> None:
    if size > Config.MAX_FILE_SIZE:
        raise ValueError(
            f"File too large: {size / 1024 / 1024:.1f} MB. Max: {Config.MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
        )


def _format_document(
    file: UploadFile, user_id: uuid.UUID, content_hash: str, size: int
) -> Document:
    s3_key = f"uploads/default-tenant/{user_id}/{uuid.uuid4()}/{file.filename}"

    return Document(
        user_id=user_id,
        filename=file.filename or "unnamed",
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        s3_key=s3_key,
        status=DocumentStatus.UPLOADING,
        content_hash=content_hash,
    )


def _check_existing_document(
    db: Session,
    user_id: uuid.UUID,
    content_hash: str,
) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id, Document.content_hash == content_hash)
        .first()
    )


async def upload_document(
    file: UploadFile,
    user_id: uuid.UUID,
    db: Session,
) -> tuple[Document, bool]:
    _check_content_type(file.content_type)

    content = await file.read()

    content_hash = hashlib.sha256(content).hexdigest()

    size = len(content)

    _check_file_size(size)

    existing = _check_existing_document(db, user_id, content_hash)

    if existing:
        if existing.status in (DocumentStatus.UPLOADING, DocumentStatus.FAILED):
            try:
                upload_document_to_s3(existing, content)
            except Exception:
                db.rollback()
                raise

            existing.status = DocumentStatus.UPLOADED
            existing.error_message = None
            db.commit()
            db.refresh(existing)
        return existing, False

    document = _format_document(file, user_id, content_hash, size)

    db.add(document)
    db.flush()

    try:
        upload_document_to_s3(document, content)
    except Exception:
        db.rollback()
        raise

    document.status = DocumentStatus.UPLOADED
    db.commit()
    db.refresh(document)

    return document, True

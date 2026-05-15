import hashlib
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.models import Document
from db.repositories.documents import db_find_by_user_and_content_hash
from db.services.document_upload import handle_existing_document, handle_new_document
from rag.config import Config


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

    existing_document = db_find_by_user_and_content_hash(db, user_id, content_hash)

    if existing_document:
        return handle_existing_document(db, existing_document, content)

    return handle_new_document(
        db=db,
        file=file,
        user_id=user_id,
        content_hash=content_hash,
        size=size,
        content=content,
    )

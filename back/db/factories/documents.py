import uuid
from uuid import UUID

from db.models import Document, DocumentStatus


def build_document(
    *,
    user_id: UUID,
    filename: str,
    mime_type: str,
    size_bytes: int,
    content_hash: str,
) -> Document:
    s3_key = f"uploads/default-tenant/{user_id}/{uuid.uuid4()}/{filename}"

    return Document(
        user_id=user_id,
        filename=filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
        s3_key=s3_key,
        status=DocumentStatus.UPLOADING,
        content_hash=content_hash,
    )

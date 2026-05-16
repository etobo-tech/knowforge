from datetime import datetime, timezone
from uuid import uuid4

from api.schemas.documents import DocumentResponse
from db.models import Document, DocumentStatus


def test_document_response_from_orm() -> None:
    document_id = uuid4()
    now = datetime.now(timezone.utc)
    document = Document(
        id=document_id,
        user_id=uuid4(),
        filename="notes.txt",
        mime_type="text/plain",
        size_bytes=12,
        s3_key="uploads/default-tenant/u1/id/notes.txt",
        status=DocumentStatus.INDEXED,
        chunks_count=2,
        content_hash="abc",
        created_at=now,
        indexed_at=now,
    )

    response = DocumentResponse.model_validate(document)

    assert response.id == document_id
    assert response.filename == "notes.txt"
    assert response.status == DocumentStatus.INDEXED.value
    assert response.chunks_count == 2

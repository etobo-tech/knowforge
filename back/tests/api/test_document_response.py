from datetime import datetime, timezone
from uuid import uuid4

import pytest

from api.document_response import build_document_response
from db.models import Document, DocumentStatus


def test_build_document_response_sets_urls_for_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = Document(
        id=uuid4(),
        user_id=uuid4(),
        filename="photo.png",
        mime_type="image/png",
        size_bytes=100,
        s3_key="uploads/u1/id/photo.png",
        status=DocumentStatus.INDEXED,
        chunks_count=1,
        content_hash="hash",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        "api.document_response.presigned_download_url",
        lambda s3_key, filename: f"https://download.test/{s3_key}",
    )
    monkeypatch.setattr(
        "api.document_response.presigned_inline_url",
        lambda s3_key: f"https://inline.test/{s3_key}",
    )

    response = build_document_response(document)

    assert response.preview_url == "https://inline.test/uploads/u1/id/photo.png"
    assert response.download_url == "https://download.test/uploads/u1/id/photo.png"


def test_build_document_response_omits_preview_for_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = Document(
        id=uuid4(),
        user_id=uuid4(),
        filename="notes.txt",
        mime_type="text/plain",
        size_bytes=10,
        s3_key="uploads/u1/id/notes.txt",
        status=DocumentStatus.INDEXED,
        chunks_count=1,
        content_hash="hash",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        "api.document_response.presigned_download_url",
        lambda s3_key, filename: "https://download.test/file",
    )

    response = build_document_response(document)

    assert response.preview_url is None
    assert response.download_url == "https://download.test/file"

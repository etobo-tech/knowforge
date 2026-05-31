import pytest
from sqlalchemy.orm import Session

from db.factories.documents import build_document
from db.models import DocumentChunk, DocumentStatus
from db.repositories.documents import db_mark_uploaded, db_persist_new_document
from rag.indexing.pipeline import index_document
from tests.helpers.constants import DEV_USER_ID


def _uploaded_image_document(db_session: Session, *, content_hash: str) -> object:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="diagram.png",
        mime_type="image/png",
        size_bytes=128,
        content_hash=content_hash,
    )
    db_persist_new_document(db_session, document)
    db_mark_uploaded(db_session, document)
    return document


def test_index_document_indexes_image(db_session: Session) -> None:
    document = _uploaded_image_document(db_session, content_hash="hash-image-ok")
    image_bytes = b"\x89PNG\r\n\x1a\nfake-image-bytes"

    index_document(db_session, document, image_bytes)
    db_session.refresh(document)

    assert document.status == DocumentStatus.INDEXED
    assert document.chunks_count == 1
    assert document.error_message is None

    chunk = (
        db_session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .one()
    )
    assert chunk.chunk_index == 0
    expected_description = (
        f"Search description for image/png ({len(image_bytes)} bytes)"
    )
    assert chunk.content == f"Image description: {expected_description}"
    assert chunk.metadata_ is not None
    assert chunk.metadata_["content_kind"] == "image"
    assert chunk.metadata_["s3_key"] == document.s3_key
    assert chunk.metadata_["search_description"] == expected_description


def test_index_document_marks_image_failed_on_empty_description(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    document = _uploaded_image_document(db_session, content_hash="hash-image-fail")

    def _raise_empty(content: bytes, mime_type: str) -> str:
        raise ValueError("Vision model returned an empty image description")

    monkeypatch.setattr(
        "rag.indexing.image.generate_image_search_description",
        _raise_empty,
    )

    ok = index_document(db_session, document, b"image-bytes")

    assert ok is False
    db_session.refresh(document)
    assert document.status == DocumentStatus.FAILED

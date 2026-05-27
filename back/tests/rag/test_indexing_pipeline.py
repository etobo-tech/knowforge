import pytest
from sqlalchemy.orm import Session

from db.factories.documents import build_document
from db.models import DocumentStatus
from db.repositories.documents import db_mark_uploaded, db_persist_new_document
from rag.indexing.pipeline import index_document
from tests.helpers.constants import DEV_USER_ID
from tests.helpers.files import plain_text_bytes


def _uploaded_document(db_session: Session, *, content_hash: str) -> object:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="pipeline.txt",
        mime_type="text/plain",
        size_bytes=20,
        content_hash=content_hash,
    )
    db_persist_new_document(db_session, document)
    db_mark_uploaded(db_session, document)
    return document


def test_index_document_indexes_plain_text(db_session: Session) -> None:
    document = _uploaded_document(db_session, content_hash="hash-pipeline-ok")

    index_document(
        db_session, document, plain_text_bytes("Pipeline content for indexing.")
    )
    db_session.refresh(document)

    assert document.status == DocumentStatus.INDEXED
    assert document.chunks_count > 0
    assert document.error_message is None


def test_index_document_skips_when_already_indexed(db_session: Session) -> None:
    document = _uploaded_document(db_session, content_hash="hash-pipeline-skip")
    content = plain_text_bytes("Already indexed content.")

    index_document(db_session, document, content)
    first_chunks = document.chunks_count
    index_document(db_session, document, content)
    db_session.refresh(document)

    assert document.status == DocumentStatus.INDEXED
    assert document.chunks_count == first_chunks


def test_index_document_marks_failed_on_unsupported_mime(db_session: Session) -> None:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="unsupported.zip",
        mime_type="application/zip",
        size_bytes=4,
        content_hash="hash-pipeline-fail",
    )
    db_persist_new_document(db_session, document)
    db_mark_uploaded(db_session, document)

    ok = index_document(db_session, document, b"data")

    assert ok is False
    db_session.refresh(document)
    assert document.status == DocumentStatus.FAILED
    assert document.error_message is not None

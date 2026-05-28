from uuid import uuid4

from sqlalchemy.orm import Session

from db.factories.documents import build_document
from db.models import Document, DocumentStatus
from db.repositories.documents import (
    db_begin_indexing,
    db_delete_document,
    db_filter_valid_source_refs,
    db_find_by_user_and_content_hash,
    db_get_document_for_user,
    db_list_documents_for_user,
    db_mark_indexing_failed,
    db_mark_uploaded,
    db_persist_new_document,
    db_save_indexed_chunks,
)
from rag.query.types import SourceRef
from tests.helpers.constants import DEV_USER_ID


def _persist_document(
    db_session: Session,
    *,
    content_hash: str = "hash-a",
    filename: str = "a.txt",
) -> Document:
    document = build_document(
        user_id=DEV_USER_ID,
        filename=filename,
        mime_type="text/plain",
        size_bytes=10,
        content_hash=content_hash,
    )
    db_persist_new_document(db_session, document)
    db_session.commit()
    db_session.refresh(document)
    return document


def test_db_find_by_user_and_content_hash(db_session: Session) -> None:
    document = _persist_document(db_session)

    found = db_find_by_user_and_content_hash(db_session, DEV_USER_ID, "hash-a")
    missing = db_find_by_user_and_content_hash(db_session, DEV_USER_ID, "missing")

    assert found is not None
    assert found.id == document.id
    assert missing is None


def test_db_mark_uploaded_updates_status(db_session: Session) -> None:
    document = _persist_document(db_session)

    updated = db_mark_uploaded(db_session, document)

    assert updated.status == DocumentStatus.UPLOADED
    assert updated.error_message is None


def test_db_begin_indexing_sets_processing(db_session: Session) -> None:
    document = _persist_document(db_session)
    db_mark_uploaded(db_session, document)

    db_begin_indexing(db_session, document)
    db_session.refresh(document)

    assert document.status == DocumentStatus.PROCESSING
    assert document.error_message is None


def test_db_save_indexed_chunks_replaces_previous_chunks(db_session: Session) -> None:
    document = _persist_document(db_session)
    db_mark_uploaded(db_session, document)
    db_begin_indexing(db_session, document)
    indexed = db_save_indexed_chunks(db_session, document, ["one", "two"])

    assert indexed.status == DocumentStatus.INDEXED
    assert indexed.chunks_count == 2
    assert indexed.indexed_at is not None
    assert len(indexed.chunks) == 2


def test_db_filter_valid_source_refs_drops_stale_chunks(db_session: Session) -> None:
    document = _persist_document(
        db_session, content_hash="hash-sources", filename="sources.txt"
    )
    db_mark_uploaded(db_session, document)
    db_begin_indexing(db_session, document)
    indexed = db_save_indexed_chunks(db_session, document, ["chunk one"])
    valid_chunk_id = indexed.chunks[0].id
    stale_chunk_id = uuid4()

    filtered = db_filter_valid_source_refs(
        db_session,
        DEV_USER_ID,
        [
            SourceRef(
                document_id=document.id,
                chunk_id=valid_chunk_id,
                score=0.9,
                quoted_text="valid",
            ),
            SourceRef(
                document_id=document.id,
                chunk_id=stale_chunk_id,
                score=0.8,
                quoted_text="stale",
            ),
        ],
    )

    assert len(filtered) == 1
    assert filtered[0].chunk_id == valid_chunk_id


def test_db_mark_indexing_failed_truncates_message(db_session: Session) -> None:
    document = _persist_document(db_session)
    long_message = "x" * 2500

    failed = db_mark_indexing_failed(db_session, document, long_message)

    assert failed.status == DocumentStatus.FAILED
    assert failed.error_message is not None
    assert len(failed.error_message) == 2000


def test_db_list_and_get_document_for_user(db_session: Session) -> None:
    document = _persist_document(
        db_session, content_hash="hash-list", filename="list.txt"
    )
    other_user = uuid4()

    listed = db_list_documents_for_user(db_session, DEV_USER_ID)
    found = db_get_document_for_user(db_session, DEV_USER_ID, document.id)
    missing = db_get_document_for_user(db_session, other_user, document.id)

    assert len(listed) == 1
    assert listed[0].id == document.id
    assert found is not None
    assert found.id == document.id
    assert missing is None


def test_db_delete_document_removes_row(db_session: Session) -> None:
    document = _persist_document(
        db_session, content_hash="hash-delete", filename="delete.txt"
    )
    document_id = document.id

    db_delete_document(db_session, document)

    assert db_get_document_for_user(db_session, DEV_USER_ID, document_id) is None

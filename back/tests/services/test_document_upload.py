from io import BytesIO

import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.factories.documents import build_document
from db.models import DocumentStatus
from db.repositories.documents import (
    db_mark_indexing_failed,
    db_mark_uploaded,
    db_persist_new_document,
)
from db.services.document_upload import handle_existing_document, handle_new_document
from tests.helpers.constants import DEV_USER_ID
from tests.helpers.files import plain_text_bytes


def _upload_file(filename: str, content: bytes, mime_type: str) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
        headers={"content-type": mime_type},
    )


def test_handle_new_document_uploads_and_indexes(
    db_session: Session,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("New document content.")
    file = _upload_file("new.txt", content, "text/plain")

    document, created = handle_new_document(
        db=db_session,
        file=file,
        user_id=DEV_USER_ID,
        content_hash="hash-new-doc",
        size=len(content),
        content=content,
    )

    assert created is True
    assert document.status == DocumentStatus.INDEXED
    assert document.chunks_count > 0


def test_handle_existing_document_reindexes_failed_state(
    db_session: Session,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("Retry indexing content.")
    existing = build_document(
        user_id=DEV_USER_ID,
        filename="retry.txt",
        mime_type="text/plain",
        size_bytes=len(content),
        content_hash="hash-retry",
    )
    db_persist_new_document(db_session, existing)
    db_mark_uploaded(db_session, existing)
    db_mark_indexing_failed(db_session, existing, "previous failure")

    document, created = handle_existing_document(db_session, existing, content)

    assert created is False
    assert document.status == DocumentStatus.INDEXED


def test_handle_existing_document_skips_reindex_when_indexed(
    db_session: Session,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("Indexed already.")
    file = _upload_file("indexed.txt", content, "text/plain")
    document, created = handle_new_document(
        db=db_session,
        file=file,
        user_id=DEV_USER_ID,
        content_hash="hash-indexed",
        size=len(content),
        content=content,
    )
    previous_chunks = document.chunks_count

    same_document, created_again = handle_existing_document(
        db_session,
        document,
        content,
    )

    assert created is True
    assert created_again is False
    assert same_document.chunks_count == previous_chunks
    assert same_document.status == DocumentStatus.INDEXED


def test_handle_existing_document_reuploads_when_still_uploading(
    db_session: Session,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("Uploading state content.")
    existing = build_document(
        user_id=DEV_USER_ID,
        filename="uploading.txt",
        mime_type="text/plain",
        size_bytes=len(content),
        content_hash="hash-uploading",
    )
    db_persist_new_document(db_session, existing)
    db_session.commit()

    document, created = handle_existing_document(db_session, existing, content)

    assert created is False
    assert document.status == DocumentStatus.INDEXED


def test_handle_existing_document_rolls_back_when_s3_fails(db_session: Session) -> None:
    content = plain_text_bytes("S3 failure on retry.")
    existing = build_document(
        user_id=DEV_USER_ID,
        filename="retry-fail.txt",
        mime_type="text/plain",
        size_bytes=len(content),
        content_hash="hash-existing-s3-fail",
    )
    db_persist_new_document(db_session, existing)
    db_session.commit()

    with pytest.raises(Exception):
        handle_existing_document(db_session, existing, content)


def test_handle_new_document_rolls_back_when_s3_fails(db_session: Session) -> None:
    content = plain_text_bytes("S3 failure content.")
    file = _upload_file("fail.txt", content, "text/plain")

    with pytest.raises(Exception):
        handle_new_document(
            db=db_session,
            file=file,
            user_id=DEV_USER_ID,
            content_hash="hash-s3-fail",
            size=len(content),
            content=content,
        )

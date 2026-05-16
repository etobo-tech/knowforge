from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.routes.documents import DEV_USER_ID
from db.factories.documents import build_document
from db.models import DocumentStatus
from db.repositories.documents import db_persist_new_document
from rag.config import Config
from tests.helpers.files import plain_text_bytes


def test_list_documents_empty(client: TestClient) -> None:
    response = client.get("/api/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_upload_get_list_and_delete_document(
    client: TestClient,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("API upload content.")
    upload = client.post(
        "/api/documents/upload",
        files={"file": ("api.txt", content, "text/plain")},
    )
    assert upload.status_code == 201
    document_id = upload.json()["id"]

    listed = client.get("/api/documents")
    fetched = client.get(f"/api/documents/{document_id}")
    deleted = client.delete(f"/api/documents/{document_id}")
    missing = client.get(f"/api/documents/{document_id}")

    assert upload.json()["status"] == DocumentStatus.INDEXED.value
    assert len(listed.json()) == 1
    assert fetched.status_code == 200
    assert fetched.json()["id"] == document_id
    assert deleted.status_code == 204
    assert missing.status_code == 404


def test_upload_duplicate_returns_200(
    client: TestClient,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("Duplicate content.")
    first = client.post(
        "/api/documents/upload",
        files={"file": ("dup.txt", content, "text/plain")},
    )
    second = client.post(
        "/api/documents/upload",
        files={"file": ("dup-copy.txt", content, "text/plain")},
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


def test_download_document_redirects(
    client: TestClient,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("Download me.")
    upload = client.post(
        "/api/documents/upload",
        files={"file": ("download.txt", content, "text/plain")},
    )
    document_id = upload.json()["id"]

    response = client.get(
        f"/api/documents/{document_id}/download", follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["location"].startswith("http")


def test_get_and_delete_unknown_document_return_404(client: TestClient) -> None:
    unknown_id = uuid4()

    get_response = client.get(f"/api/documents/{unknown_id}")
    delete_response = client.delete(f"/api/documents/{unknown_id}")

    assert get_response.status_code == 404
    assert delete_response.status_code == 404


def test_upload_rejects_unsupported_mime_type(client: TestClient) -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("archive.zip", b"zip", "application/zip")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_rejects_oversized_file(client: TestClient) -> None:
    oversized = b"x" * (Config.MAX_FILE_SIZE + 1)
    response = client.post(
        "/api/documents/upload",
        files={"file": ("big.txt", oversized, "text/plain")},
    )

    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]


def test_download_returns_503_when_presign_fails(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="broken.txt",
        mime_type="text/plain",
        size_bytes=4,
        content_hash="hash-broken-download",
    )
    db_persist_new_document(db_session, document)
    db_session.commit()

    def raise_presign_error(*_args: object, **_kwargs: object) -> str:
        raise RuntimeError("presign failed")

    monkeypatch.setattr(
        "api.routes.documents.presigned_download_url",
        raise_presign_error,
    )

    response = client.get(f"/api/documents/{document.id}/download")

    assert response.status_code == 503


def test_upload_returns_500_on_unexpected_error(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def raise_unexpected(
        *_args: object, **_kwargs: object
    ) -> tuple[object, bool]:
        raise RuntimeError("unexpected")

    monkeypatch.setattr("api.routes.documents.upload_document", raise_unexpected)

    response = client.post(
        "/api/documents/upload",
        files={"file": ("fail.txt", b"data", "text/plain")},
    )

    assert response.status_code == 500
    assert "unexpected" in response.json()["detail"]


def test_delete_ignores_s3_errors(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="delete.txt",
        mime_type="text/plain",
        size_bytes=4,
        content_hash="hash-delete-s3",
    )
    db_persist_new_document(db_session, document)
    db_session.commit()

    def raise_delete_error(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("delete failed")

    monkeypatch.setattr(
        "api.routes.documents.delete_object_from_s3",
        raise_delete_error,
    )

    response = client.delete(f"/api/documents/{document.id}")

    assert response.status_code == 204
    assert client.get(f"/api/documents/{document.id}").status_code == 404

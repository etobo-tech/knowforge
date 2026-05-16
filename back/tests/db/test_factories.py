from db.factories.documents import build_document
from db.models import DocumentStatus
from tests.helpers.constants import DEV_USER_ID


def test_build_document_sets_expected_fields() -> None:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="report.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        content_hash="hash-1",
    )

    assert document.user_id == DEV_USER_ID
    assert document.filename == "report.pdf"
    assert document.mime_type == "application/pdf"
    assert document.size_bytes == 1024
    assert document.content_hash == "hash-1"
    assert document.status == DocumentStatus.UPLOADING
    assert document.s3_key.startswith(f"uploads/default-tenant/{DEV_USER_ID}/")

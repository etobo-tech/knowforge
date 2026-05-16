import boto3

from db.factories.documents import build_document
from rag.config import Config
from rag.s3 import (
    _safe_attachment_filename,
    delete_object_from_s3,
    presigned_download_url,
    upload_document_to_s3,
)
from tests.helpers.constants import DEV_USER_ID
from tests.helpers.files import plain_text_bytes


def test_safe_attachment_filename_sanitizes_path_and_quotes() -> None:
    assert _safe_attachment_filename('folder/evil"name.pdf') == "evil'name.pdf"


def test_upload_delete_and_presign_roundtrip(s3_mock: None) -> None:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="notes.txt",
        mime_type="text/plain",
        size_bytes=20,
        content_hash="hash-s3",
    )
    content = plain_text_bytes()

    upload_document_to_s3(document, content)
    url = presigned_download_url(document.s3_key, document.filename)
    delete_object_from_s3(document.s3_key)

    s3 = boto3.client("s3", region_name=Config.S3_REGION)
    objects = s3.list_objects_v2(Bucket=Config.S3_BUCKET).get("Contents", [])

    assert url.startswith("http")
    assert not any(item["Key"] == document.s3_key for item in objects)

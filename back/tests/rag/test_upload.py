from io import BytesIO

import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

from rag.upload import upload_document
from tests.helpers.constants import DEV_USER_ID
from tests.helpers.files import plain_text_bytes


def _upload_file(filename: str, content: bytes, mime_type: str | None) -> UploadFile:
    headers = {"content-type": mime_type} if mime_type is not None else {}
    return UploadFile(filename=filename, file=BytesIO(content), headers=headers)


@pytest.mark.asyncio
async def test_upload_document_creates_indexed_document(
    db_session: Session,
    s3_mock: None,
) -> None:
    content = plain_text_bytes("Upload orchestration content.")
    file = _upload_file("upload.txt", content, "text/plain")

    document, created = await upload_document(file, DEV_USER_ID, db_session)

    assert created is True
    assert document.chunks_count > 0


@pytest.mark.asyncio
async def test_upload_document_requires_content_type(db_session: Session) -> None:
    file = _upload_file("no-type.txt", b"data", None)

    with pytest.raises(ValueError, match="Missing content type"):
        await upload_document(file, DEV_USER_ID, db_session)

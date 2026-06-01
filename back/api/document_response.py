from db.models import Document
from api.schemas.documents import DocumentResponse
from rag.mime import is_image_mime
from rag.s3 import presigned_download_url, presigned_inline_url


def build_document_response(document: Document) -> DocumentResponse:
    preview_url: str | None = None
    download_url: str | None = None

    if document.s3_key:
        try:
            download_url = presigned_download_url(document.s3_key, document.filename)
        except Exception:
            download_url = None
        if is_image_mime(document.mime_type):
            try:
                preview_url = presigned_inline_url(document.s3_key)
            except Exception:
                preview_url = None

    return DocumentResponse.model_validate(document).model_copy(
        update={
            "preview_url": preview_url,
            "download_url": download_url,
        }
    )

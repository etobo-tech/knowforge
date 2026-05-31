from sqlalchemy.orm import Session

from db.models import Document, DocumentStatus
from rag.indexing.image import index_image_document
from rag.indexing.text import index_text_document
from rag.mime import is_image_mime


def index_document(db: Session, document: Document, content: bytes) -> bool:
    """Index document content. Returns False if indexing failed (status=FAILED)."""
    if document.status == DocumentStatus.INDEXED:
        return True

    if is_image_mime(document.mime_type):
        return index_image_document(db=db, document=document, content=content)

    return index_text_document(db=db, document=document, content=content)

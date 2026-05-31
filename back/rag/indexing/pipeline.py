from sqlalchemy.orm import Session

from db.models import Document, DocumentStatus
from rag.indexing.text import index_text_document


def index_document(db: Session, document: Document, content: bytes) -> bool:
    """Index document content. Returns False if indexing failed (status=FAILED)."""
    if document.status == DocumentStatus.INDEXED:
        return True

    return index_text_document(db=db, document=document, content=content)

from sqlalchemy.orm import Session

from db.models import Document, DocumentStatus
from db.repositories.documents import (
    db_begin_indexing,
    db_mark_indexing_failed,
    db_save_indexed_chunks,
)
from rag.indexing.chunk import chunk_text
from rag.indexing.embed import embed_texts
from rag.indexing.extract import extract_text
from rag.vector_store import sync_indexed_document_vectors


def index_document(db: Session, document: Document, content: bytes) -> bool:
    """Index document content. Returns False if indexing failed (status=FAILED)."""
    if document.status == DocumentStatus.INDEXED:
        return True

    db_begin_indexing(db, document)

    try:
        text = extract_text(content, document.mime_type)
        chunk_texts = chunk_text(text)
        embeddings = embed_texts(chunk_texts)
        db_save_indexed_chunks(db, document, chunk_texts)
        db.refresh(document)
        sync_indexed_document_vectors(db, document, embeddings)
        return True
    except Exception as exc:
        db_mark_indexing_failed(db, document, str(exc))
        db.refresh(document)
        return False

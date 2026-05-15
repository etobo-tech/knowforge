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


def index_document(db: Session, document: Document, content: bytes) -> None:
    if document.status == DocumentStatus.INDEXED:
        return

    db_begin_indexing(db, document)

    try:
        text = extract_text(content, document.mime_type)
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)
        chunk_data = list(zip(chunks, embeddings, strict=True))
        db_save_indexed_chunks(db, document, chunk_data)
    except Exception as exc:
        db_mark_indexing_failed(db, document, str(exc))
        raise

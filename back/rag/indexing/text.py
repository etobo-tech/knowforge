from sqlalchemy.orm import Session

from db.models import Document, DocumentStatus
from db.repositories.documents import (
    db_begin_indexing,
    db_list_chunks_for_document,
    db_mark_indexing_failed,
    db_save_indexed_chunks,
)
from rag.indexing.chunk import chunk_text
from rag.indexing.embed import embed_texts
from rag.indexing.extract import extract_text
from rag.vector_store import sync_document_vectors


def index_text_document(db: Session, document: Document, content: bytes) -> bool:
    if document.status == DocumentStatus.INDEXED:
        return True

    db_begin_indexing(db, document)

    try:
        text = extract_text(content, document.mime_type)
        chunk_texts = chunk_text(text)
        embeddings = embed_texts(chunk_texts)
        db_save_indexed_chunks(db=db, document=document, chunk_texts=chunk_texts)
        db.refresh(document)
        chunks = db_list_chunks_for_document(db=db, document_id=document.id)
        sync_document_vectors(
            document=document,
            chunks=chunks,
            embeddings=embeddings,
        )
        return True
    except Exception as exc:
        db_mark_indexing_failed(db=db, document=document, message=str(exc))
        db.refresh(document)
        return False

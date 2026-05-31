from sqlalchemy.orm import Session

from db.models import Document, DocumentStatus
from db.repositories.documents import (
    db_begin_indexing,
    db_list_chunks_for_document,
    db_mark_indexing_failed,
    db_save_indexed_image_chunk,
)
from llama_index.core.llms import ChatMessage, ImageBlock, MessageRole, TextBlock
from rag.config import Config
from rag.indexing.embed import embed_texts
from rag.llama_settings import get_vision_llm
from rag.vector_store import sync_image_document_vectors


def _vision_description_message(content: bytes, mime_type: str) -> ChatMessage:
    return ChatMessage(
        role=MessageRole.USER,
        blocks=[
            TextBlock(text=Config.IMAGE_SEARCH_DESCRIPTION_PROMPT),
            ImageBlock(
                image=content,
                image_mimetype=mime_type,
                detail=Config.IMAGE_INDEX_DETAIL,
            ),
        ],
    )


def generate_image_search_description(content: bytes, mime_type: str) -> str:
    llm = get_vision_llm(detail=Config.IMAGE_INDEX_DETAIL)
    response = llm.chat(messages=[_vision_description_message(content, mime_type)])
    description = str(response.message.content).strip()

    if not description:
        raise ValueError("Vision model returned an empty image description")
    return description


def _persist_indexed_image(
    db: Session,
    document: Document,
    content: bytes,
) -> None:
    search_description = generate_image_search_description(
        content=content,
        mime_type=document.mime_type,
    )
    embeddings = embed_texts([search_description])

    db_save_indexed_image_chunk(
        db=db,
        document=document,
        search_description=search_description,
    )

    db.refresh(document)
    chunks = db_list_chunks_for_document(db=db, document_id=document.id)

    sync_image_document_vectors(
        document=document,
        chunks=chunks,
        embeddings=embeddings,
    )


def index_image_document(db: Session, document: Document, content: bytes) -> bool:
    if document.status == DocumentStatus.INDEXED:
        return True

    db_begin_indexing(db, document)

    try:
        _persist_indexed_image(db=db, document=document, content=content)
        return True
    except Exception as exc:
        db_mark_indexing_failed(db, document, str(exc))
        db.refresh(document)
        return False

"""PGVectorStore: index sync, delete, and retrieval filters."""

from uuid import UUID

from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.vector_stores.types import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Document, DocumentChunk
from rag.config import Config
from utils import get_pgvector_connection_strings

_store: PGVectorStore | None = None


def get_pg_vector_store() -> PGVectorStore:
    global _store
    if _store is None:
        sync_url, async_url = get_pgvector_connection_strings()
        _store = PGVectorStore.from_params(
            connection_string=sync_url,
            async_connection_string=async_url,
            table_name=Config.VECTOR_TABLE_NAME,
            embed_dim=Config.EMBEDDING_DIMENSION,
            use_jsonb=True,
            perform_setup=True,
        )
    return _store


def user_metadata_filters(user_id: UUID) -> MetadataFilters:
    return MetadataFilters(
        filters=[
            MetadataFilter(
                key="user_id",
                value=str(user_id),
                operator=FilterOperator.EQ,
            )
        ]
    )


def _document_metadata_filters(document_id: UUID) -> MetadataFilters:
    return MetadataFilters(
        filters=[
            MetadataFilter(
                key="document_id",
                value=str(document_id),
                operator=FilterOperator.EQ,
            )
        ]
    )


def delete_document_vectors(document_id: UUID) -> None:
    get_pg_vector_store().delete_nodes(filters=_document_metadata_filters(document_id))


def sync_document_vectors(
    document: Document,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")

    store = get_pg_vector_store()
    delete_document_vectors(document.id)

    if not chunks:
        return

    nodes: list[BaseNode] = [
        TextNode(
            id_=str(chunk.id),
            text=chunk.content,
            embedding=embedding,
            metadata={
                "user_id": str(document.user_id),
                "document_id": str(document.id),
                "chunk_id": str(chunk.id),
                "filename": document.filename,
                "page_number": chunk.page_number,
            },
        )
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]
    store.add(nodes)


def sync_indexed_document_vectors(
    db: Session,
    document: Document,
    embeddings: list[list[float]],
) -> None:
    chunks = (
        db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
        )
        .scalars()
        .all()
    )
    sync_document_vectors(document, list(chunks), embeddings)

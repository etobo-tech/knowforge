"""PGVectorStore: index sync, delete, and retrieval filters."""

from uuid import UUID

from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.vector_stores.types import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.vector_stores.postgres import PGVectorStore

from db.models import Document, DocumentChunk
from rag.config import Config
from utils import get_pgvector_connection_strings

_text_store: PGVectorStore | None = None
_image_store: PGVectorStore | None = None


def _build_pg_vector_store(*, table_name: str) -> PGVectorStore:
    sync_url, async_url = get_pgvector_connection_strings()
    return PGVectorStore.from_params(
        connection_string=sync_url,
        async_connection_string=async_url,
        table_name=table_name,
        embed_dim=Config.EMBEDDING_DIMENSION,
        use_jsonb=True,
        perform_setup=True,
    )


def get_pg_vector_store() -> PGVectorStore:
    global _text_store
    if _text_store is None:
        _text_store = _build_pg_vector_store(table_name=Config.VECTOR_TABLE_NAME)
    return _text_store


def get_pg_image_vector_store() -> PGVectorStore:
    global _image_store
    if _image_store is None:
        _image_store = _build_pg_vector_store(table_name=Config.IMAGE_VECTOR_TABLE_NAME)
    return _image_store


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


def delete_text_document_vectors(document_id: UUID) -> None:
    get_pg_vector_store().delete_nodes(filters=_document_metadata_filters(document_id))


def delete_image_document_vectors(document_id: UUID) -> None:
    get_pg_image_vector_store().delete_nodes(
        filters=_document_metadata_filters(document_id)
    )


def delete_document_vectors(document_id: UUID) -> None:
    delete_text_document_vectors(document_id)
    delete_image_document_vectors(document_id)


def _text_node_from_chunk(
    *,
    document: Document,
    chunk: DocumentChunk,
    embedding: list[float],
) -> TextNode:
    return TextNode(
        id_=str(chunk.id),
        text=chunk.content,
        embedding=embedding,
        metadata={
            "user_id": str(document.user_id),
            "document_id": str(document.id),
            "chunk_id": str(chunk.id),
            "filename": document.filename,
            "page_number": chunk.page_number,
            "content_kind": Config.CONTENT_KIND_TEXT,
        },
    )


def _image_node_from_chunk(
    *,
    document: Document,
    chunk: DocumentChunk,
    embedding: list[float],
) -> TextNode:
    metadata = chunk.metadata_ or {}
    search_description = metadata.get("search_description") or chunk.content
    return TextNode(
        id_=str(chunk.id),
        text=str(search_description),
        embedding=embedding,
        metadata={
            "user_id": str(document.user_id),
            "document_id": str(document.id),
            "chunk_id": str(chunk.id),
            "s3_key": document.s3_key,
            "filename": document.filename,
            "mime_type": document.mime_type,
            "content_kind": Config.CONTENT_KIND_IMAGE,
        },
    )


def sync_document_vectors(
    document: Document,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")

    store = get_pg_vector_store()
    delete_text_document_vectors(document.id)

    if not chunks:
        return

    nodes: list[BaseNode] = [
        _text_node_from_chunk(document=document, chunk=chunk, embedding=embedding)
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]
    store.add(nodes)


def sync_image_document_vectors(
    document: Document,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")

    store = get_pg_image_vector_store()
    delete_image_document_vectors(document.id)

    if not chunks:
        return

    nodes: list[BaseNode] = [
        _image_node_from_chunk(document=document, chunk=chunk, embedding=embedding)
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]
    store.add(nodes)

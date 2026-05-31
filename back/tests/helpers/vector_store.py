"""In-memory stand-in for PGVectorStore used in tests (SQLite has no pgvector)."""

from uuid import UUID

from llama_index.core.schema import TextNode

from db.models import Document, DocumentChunk
from rag.config import Config

_text_nodes: list[TextNode] = []
_image_nodes: list[TextNode] = []


def reset_fake_vector_store() -> None:
    _text_nodes.clear()
    _image_nodes.clear()


def fake_sync_document_vectors(
    document: Document,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
) -> None:
    global _text_nodes
    doc_id = str(document.id)
    _text_nodes = [
        node for node in _text_nodes if node.metadata.get("document_id") != doc_id
    ]

    for chunk, embedding in zip(chunks, embeddings, strict=True):
        _text_nodes.append(
            TextNode(
                id_=str(chunk.id),
                text=chunk.content,
                embedding=embedding,
                metadata={
                    "user_id": str(document.user_id),
                    "document_id": doc_id,
                    "chunk_id": str(chunk.id),
                    "filename": document.filename,
                    "page_number": chunk.page_number,
                },
            )
        )


def fake_sync_image_document_vectors(
    document: Document,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
) -> None:
    global _image_nodes
    doc_id = str(document.id)
    _image_nodes = [
        node for node in _image_nodes if node.metadata.get("document_id") != doc_id
    ]

    for chunk, embedding in zip(chunks, embeddings, strict=True):
        chunk_metadata = chunk.metadata_ or {}
        search_description = chunk_metadata.get("search_description") or chunk.content
        _image_nodes.append(
            TextNode(
                id_=str(chunk.id),
                text=str(search_description),
                embedding=embedding,
                metadata={
                    "user_id": str(document.user_id),
                    "document_id": doc_id,
                    "chunk_id": str(chunk.id),
                    "filename": document.filename,
                    "s3_key": document.s3_key,
                    "mime_type": document.mime_type,
                    "content_kind": Config.CONTENT_KIND_IMAGE,
                },
            )
        )


def fake_delete_document_vectors(document_id: UUID) -> None:
    global _text_nodes, _image_nodes
    doc_id = str(document_id)
    _text_nodes = [
        node for node in _text_nodes if node.metadata.get("document_id") != doc_id
    ]
    _image_nodes = [
        node for node in _image_nodes if node.metadata.get("document_id") != doc_id
    ]


def fake_query_similar_vectors(
    user_id: UUID,
    query_embedding: list[float],
    *,
    top_k: int = 5,
) -> list[tuple[TextNode, float | None]]:
    """Test-only cosine search over the in-memory fake text store."""
    import math

    user_key = str(user_id)
    scored: list[tuple[float, TextNode]] = []
    for node in _text_nodes:
        if node.metadata.get("user_id") != user_key:
            continue
        embedding = node.embedding
        if embedding is None:
            continue
        dot = sum(a * b for a, b in zip(query_embedding, embedding, strict=True))
        left_norm = math.sqrt(sum(value * value for value in query_embedding))
        right_norm = math.sqrt(sum(value * value for value in embedding))
        score = dot / (left_norm * right_norm) if left_norm and right_norm else 0.0
        scored.append((score, node))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [(node, score) for score, node in scored[:top_k]]


def patch_vector_store(monkeypatch) -> None:
    monkeypatch.setattr(
        "rag.vector_store.sync_document_vectors",
        fake_sync_document_vectors,
    )
    monkeypatch.setattr(
        "rag.indexing.text.sync_document_vectors",
        fake_sync_document_vectors,
    )
    monkeypatch.setattr(
        "rag.vector_store.sync_image_document_vectors",
        fake_sync_image_document_vectors,
    )
    monkeypatch.setattr(
        "rag.vector_store.delete_document_vectors",
        fake_delete_document_vectors,
    )
    monkeypatch.setattr(
        "rag.vector_store.get_pg_vector_store",
        lambda: (_ for _ in ()).throw(
            RuntimeError("PGVectorStore not available in tests")
        ),
    )
    monkeypatch.setattr(
        "rag.vector_store.get_pg_image_vector_store",
        lambda: (_ for _ in ()).throw(
            RuntimeError("PGVectorStore not available in tests")
        ),
    )

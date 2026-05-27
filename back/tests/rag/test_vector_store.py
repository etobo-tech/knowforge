from uuid import uuid4

from sqlalchemy.orm import Session

from db.factories.documents import build_document
from db.models import Document, DocumentChunk
from db.repositories.documents import (
    db_mark_uploaded,
    db_persist_new_document,
)
from rag import vector_store
from rag.indexing.pipeline import index_document
from rag.vector_store import (
    delete_document_vectors as real_delete_document_vectors,
    sync_document_vectors as real_sync_document_vectors,
    user_metadata_filters,
)
from tests.helpers.constants import DEV_USER_ID
from tests.helpers.embeddings import deterministic_embeddings
from tests.helpers.files import plain_text_bytes
from tests.helpers.vector_store import fake_query_similar_vectors


def _indexed_refund_policy(db_session: Session) -> None:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="refund_policy.txt",
        mime_type="text/plain",
        size_bytes=80,
        content_hash="hash-vector-refund",
    )
    db_persist_new_document(db_session, document)
    db_mark_uploaded(db_session, document)
    index_document(
        db_session,
        document,
        plain_text_bytes(
            "Refund policy: customers may request a refund within 30 days."
        ),
    )


def test_fake_vector_store_returns_indexed_chunks(db_session: Session) -> None:
    _indexed_refund_policy(db_session)

    query_embedding = deterministic_embeddings(["refund policy"])[0]
    results = fake_query_similar_vectors(
        DEV_USER_ID,
        query_embedding,
        top_k=3,
    )

    assert len(results) >= 1
    node, score = results[0]
    assert "refund" in node.get_content().lower()
    assert node.metadata["filename"] == "refund_policy.txt"
    assert score is not None


class FakePgVectorStore:
    def __init__(self) -> None:
        self.added = []
        self.deleted_filters = []

    def add(self, nodes):
        self.added.extend(nodes)

    def delete_nodes(self, *, filters):
        self.deleted_filters.append(filters)


def test_user_metadata_filters_scopes_retrieval_to_user() -> None:
    filters = user_metadata_filters(DEV_USER_ID)

    only_filter = filters.filters[0]
    assert only_filter.key == "user_id"
    assert only_filter.value == str(DEV_USER_ID)


def test_delete_document_vectors_uses_document_filter(monkeypatch) -> None:
    store = FakePgVectorStore()
    monkeypatch.setattr(vector_store, "get_pg_vector_store", lambda: store)

    document_id = _indexed_document_id()
    real_delete_document_vectors(document_id)

    deleted_filter = store.deleted_filters[0].filters[0]
    assert deleted_filter.key == "document_id"
    assert deleted_filter.value == str(document_id)


def test_sync_document_vectors_adds_text_nodes(
    db_session: Session, monkeypatch
) -> None:
    store = FakePgVectorStore()
    monkeypatch.setattr(vector_store, "get_pg_vector_store", lambda: store)
    monkeypatch.setattr(
        vector_store, "delete_document_vectors", real_delete_document_vectors
    )
    document, chunks = _document_with_chunks(db_session)

    real_sync_document_vectors(document, chunks, [[0.1, 0.2], [0.3, 0.4]])

    assert len(store.added) == 2
    assert store.added[0].metadata["user_id"] == str(DEV_USER_ID)
    assert store.added[0].metadata["document_id"] == str(document.id)
    assert store.added[0].metadata["chunk_id"] == str(chunks[0].id)


def test_sync_document_vectors_rejects_embedding_mismatch(
    db_session: Session,
) -> None:
    document, chunks = _document_with_chunks(db_session)

    try:
        real_sync_document_vectors(document, chunks, [[0.1, 0.2]])
    except ValueError as exc:
        assert "length mismatch" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_sync_document_vectors_deletes_existing_vectors_for_empty_chunks(
    monkeypatch,
) -> None:
    store = FakePgVectorStore()
    monkeypatch.setattr(vector_store, "get_pg_vector_store", lambda: store)
    monkeypatch.setattr(
        vector_store, "delete_document_vectors", real_delete_document_vectors
    )
    document = build_document(
        user_id=DEV_USER_ID,
        filename="empty.txt",
        mime_type="text/plain",
        size_bytes=0,
        content_hash="hash-vector-empty",
    )
    document.id = uuid4()

    real_sync_document_vectors(document, [], [])

    assert store.added == []
    assert len(store.deleted_filters) == 1


def _indexed_document_id():
    return uuid4()


def _document_with_chunks(
    db_session: Session,
) -> tuple[Document, list[DocumentChunk]]:
    document = build_document(
        user_id=DEV_USER_ID,
        filename="chunks.txt",
        mime_type="text/plain",
        size_bytes=10,
        content_hash="hash-vector-chunks",
    )
    db_persist_new_document(db_session, document)
    db_mark_uploaded(db_session, document)
    chunks = [
        DocumentChunk(document_id=document.id, chunk_index=0, content="First chunk"),
        DocumentChunk(document_id=document.id, chunk_index=1, content="Second chunk"),
    ]
    db_session.add_all(chunks)
    db_session.flush()
    return document, chunks

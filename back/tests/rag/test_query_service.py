from datetime import datetime, timezone
from uuid import uuid4

from llama_index.core.schema import NodeWithScore, TextNode
from sqlalchemy.orm import Session

from db.models import Message, MessageRole
from db.repositories.chats import db_create_chat
from rag.query import service
from rag.query.service import (
    NO_INDEXED_DOCUMENTS_REPLY,
    NO_RETRIEVAL_CONTEXT_REPLY,
    generate_chat_reply,
)
from tests.helpers.constants import DEV_USER_ID


def test_generate_chat_reply_without_indexed_documents(db_session: Session) -> None:
    chat = db_create_chat(db_session, DEV_USER_ID, title="Empty KB")

    reply = generate_chat_reply(
        db_session,
        DEV_USER_ID,
        "What is the refund policy?",
        [],
    )

    assert reply.content == NO_INDEXED_DOCUMENTS_REPLY
    assert reply.sources == []


def _source_node(*, chunk_id: str | None = None) -> NodeWithScore:
    document_id = uuid4()
    chunk_uuid = chunk_id or str(uuid4())
    return NodeWithScore(
        node=TextNode(
            text="Relevant source excerpt",
            metadata={
                "document_id": str(document_id),
                "chunk_id": chunk_uuid,
            },
        ),
        score=0.75,
    )


def test_sources_from_nodes_skips_duplicates_and_missing_metadata() -> None:
    chunk_id = str(uuid4())

    sources = service.sources_from_nodes(
        [
            _source_node(chunk_id=chunk_id),
            _source_node(chunk_id=chunk_id),
            NodeWithScore(node=TextNode(text="missing metadata"), score=None),
        ]
    )

    assert len(sources) == 1
    assert str(sources[0].chunk_id) == chunk_id
    assert sources[0].quoted_text == "Relevant source excerpt"
    assert sources[0].score == 0.75


def test_sources_from_nodes_skips_invalid_uuids() -> None:
    sources = service.sources_from_nodes(
        [
            NodeWithScore(
                node=TextNode(
                    text="bad ids",
                    metadata={
                        "document_id": "not-a-uuid",
                        "chunk_id": "also-not-a-uuid",
                    },
                ),
                score=0.5,
            )
        ]
    )

    assert sources == []


def test_build_memory_keeps_user_and_assistant_messages() -> None:
    messages = [
        Message(
            role=MessageRole.USER,
            content="Question",
            created_at=datetime.now(timezone.utc),
        ),
        Message(
            role=MessageRole.ASSISTANT,
            content="Answer",
            created_at=datetime.now(timezone.utc),
        ),
        Message(
            role=MessageRole.SYSTEM,
            content="Ignored",
            created_at=datetime.now(timezone.utc),
        ),
    ]

    memory = service.build_memory(messages)

    assert [message.content for message in memory.get()] == ["Question", "Answer"]


def test_generate_chat_reply_returns_fallback_without_retrieved_context(
    db_session: Session,
    monkeypatch,
) -> None:
    chat = db_create_chat(db_session, DEV_USER_ID, title="Empty context")

    class FakeRetriever:
        def retrieve(self, query_bundle):
            return []

    monkeypatch.setattr(service, "db_user_has_indexed_chunks", lambda db, user_id: True)
    monkeypatch.setattr(service, "configure_llama_index", lambda: None)
    monkeypatch.setattr(
        service, "create_user_retriever", lambda user_id: FakeRetriever()
    )

    reply = generate_chat_reply(db_session, DEV_USER_ID, "Where is context?", [])

    assert reply.content == NO_RETRIEVAL_CONTEXT_REPLY
    assert reply.sources == []


def test_generate_chat_reply_returns_content_and_sources(
    db_session: Session,
    monkeypatch,
) -> None:
    chat = db_create_chat(db_session, DEV_USER_ID, title="With context")
    source_node = _source_node()

    class FakeRetriever:
        def retrieve(self, query_bundle):
            return [source_node]

    class FakeEngine:
        def chat(self, user_message: str):
            return type(
                "Response",
                (),
                {"response": "Use the refund policy.", "source_nodes": [source_node]},
            )()

    monkeypatch.setattr(service, "db_user_has_indexed_chunks", lambda db, user_id: True)
    monkeypatch.setattr(service, "configure_llama_index", lambda: None)
    monkeypatch.setattr(
        service, "create_user_retriever", lambda user_id: FakeRetriever()
    )
    monkeypatch.setattr(
        service,
        "db_filter_valid_source_refs",
        lambda db, user_id, sources: sources,
    )
    monkeypatch.setattr(
        service.ContextChatEngine,
        "from_defaults",
        lambda **kwargs: FakeEngine(),
    )

    reply = generate_chat_reply(db_session, DEV_USER_ID, "Refund?", [])

    assert reply.content == "Use the refund policy."
    assert len(reply.sources) == 1


def test_generate_chat_reply_returns_fallback_for_empty_model_response(
    db_session: Session,
    monkeypatch,
) -> None:
    chat = db_create_chat(db_session, DEV_USER_ID, title="Empty response")
    source_node = _source_node()

    class FakeRetriever:
        def retrieve(self, query_bundle):
            return [source_node]

    class FakeEngine:
        def chat(self, user_message: str):
            return type(
                "Response",
                (),
                {"response": "Empty Response", "source_nodes": [source_node]},
            )()

    monkeypatch.setattr(service, "db_user_has_indexed_chunks", lambda db, user_id: True)
    monkeypatch.setattr(service, "configure_llama_index", lambda: None)
    monkeypatch.setattr(
        service, "create_user_retriever", lambda user_id: FakeRetriever()
    )
    monkeypatch.setattr(
        service,
        "db_filter_valid_source_refs",
        lambda db, user_id, sources: sources,
    )
    monkeypatch.setattr(
        service.ContextChatEngine,
        "from_defaults",
        lambda **kwargs: FakeEngine(),
    )

    reply = generate_chat_reply(db_session, DEV_USER_ID, "Refund?", [])

    assert reply.content == NO_RETRIEVAL_CONTEXT_REPLY
    assert len(reply.sources) == 1


def test_sources_from_nodes_includes_image_metadata() -> None:
    chunk_id = str(uuid4())
    document_id = str(uuid4())
    sources = service.sources_from_nodes(
        [
            NodeWithScore(
                node=TextNode(
                    text="A chart showing quarterly revenue",
                    metadata={
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "content_kind": "image",
                        "s3_key": "uploads/chart.png",
                        "filename": "chart.png",
                        "mime_type": "image/png",
                    },
                ),
                score=0.9,
            )
        ]
    )

    assert len(sources) == 1
    assert sources[0].content_kind == "image"
    assert sources[0].s3_key == "uploads/chart.png"
    assert sources[0].filename == "chart.png"


def test_generate_chat_reply_uses_multimodal_path_for_image_nodes(
    db_session: Session,
    monkeypatch,
) -> None:
    image_node = NodeWithScore(
        node=TextNode(
            text="Chart description",
            metadata={
                "document_id": str(uuid4()),
                "chunk_id": str(uuid4()),
                "content_kind": "image",
                "s3_key": "uploads/chart.png",
                "filename": "chart.png",
                "mime_type": "image/png",
            },
        ),
        score=0.8,
    )

    class FakeRetriever:
        def retrieve(self, query_bundle):
            return [image_node]

    monkeypatch.setattr(service, "db_user_has_indexed_chunks", lambda db, user_id: True)
    monkeypatch.setattr(service, "configure_llama_index", lambda: None)
    monkeypatch.setattr(
        service, "create_user_retriever", lambda user_id: FakeRetriever()
    )
    monkeypatch.setattr(
        service,
        "generate_multimodal_reply",
        lambda **kwargs: "The chart shows growth.",
    )
    monkeypatch.setattr(
        service,
        "db_filter_valid_source_refs",
        lambda db, user_id, sources: sources,
    )

    reply = generate_chat_reply(db_session, DEV_USER_ID, "Explain the chart", [])

    assert reply.content == "The chart shows growth."
    assert len(reply.sources) == 1
    assert reply.sources[0].content_kind == "image"

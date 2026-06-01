from uuid import UUID

from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.schema import NodeWithScore, QueryBundle
from sqlalchemy.orm import Session

from db.models import Message
from db.repositories.documents import (
    db_filter_valid_source_refs,
    db_user_has_indexed_chunks,
)
from rag.llama_settings import configure_llama_index
from rag.query.memory import build_memory
from rag.query.multimodal_chat import generate_multimodal_reply
from rag.query.prompts import (
    NO_INDEXED_DOCUMENTS_REPLY,
    NO_RETRIEVAL_CONTEXT_REPLY,
)
from rag.query.retriever import create_user_retriever
from rag.query.sources import (
    is_image_node,
    sources_from_nodes,
)
from rag.query.text_chat import generate_text_reply
from rag.query.types import ChatReply, SourceRef

# Re-exported for tests that monkeypatch or import helpers from this module.
__all__ = [
    "ContextChatEngine",
    "NO_INDEXED_DOCUMENTS_REPLY",
    "NO_RETRIEVAL_CONTEXT_REPLY",
    "build_memory",
    "sources_from_nodes",
    "configure_llama_index",
    "create_user_retriever",
    "db_filter_valid_source_refs",
    "db_user_has_indexed_chunks",
    "generate_chat_reply",
    "generate_multimodal_reply",
]


def _reply_sources(
    db: Session,
    user_id: UUID,
    nodes: list[NodeWithScore],
) -> list[SourceRef]:
    return db_filter_valid_source_refs(db, user_id, sources_from_nodes(nodes))


def generate_chat_reply(
    db: Session,
    user_id: UUID,
    user_message: str,
    prior_messages: list[Message],
) -> ChatReply:
    if not db_user_has_indexed_chunks(db, user_id):
        return ChatReply(content=NO_INDEXED_DOCUMENTS_REPLY, sources=[])

    configure_llama_index()
    retriever = create_user_retriever(user_id)
    retrieved_nodes = retriever.retrieve(QueryBundle(query_str=user_message))

    if not retrieved_nodes:
        return ChatReply(content=NO_RETRIEVAL_CONTEXT_REPLY, sources=[])

    has_image_context = any(is_image_node(node) for node in retrieved_nodes)

    if has_image_context:
        content = generate_multimodal_reply(
            user_message=user_message,
            prior_messages=prior_messages,
            source_nodes=retrieved_nodes,
        )
        source_nodes = retrieved_nodes
    else:
        content, source_nodes = generate_text_reply(
            user_message=user_message,
            prior_messages=prior_messages,
            retriever=retriever,
        )

    if not source_nodes:
        return ChatReply(content=NO_RETRIEVAL_CONTEXT_REPLY, sources=[])

    if not content or content == "Empty Response":
        return ChatReply(
            content=NO_RETRIEVAL_CONTEXT_REPLY,
            sources=_reply_sources(db, user_id, source_nodes),
        )

    return ChatReply(
        content=content,
        sources=_reply_sources(db, user_id, source_nodes),
    )

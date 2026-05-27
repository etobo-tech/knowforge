from uuid import UUID

from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.llms import ChatMessage, MessageRole as LlamaMessageRole
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.schema import NodeWithScore
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from sqlalchemy.orm import Session

from db.models import Chat, Message, MessageRole
from db.repositories.documents import db_user_has_indexed_chunks
from rag.config import Config
from rag.query.retriever import create_user_retriever
from rag.query.types import ChatReply, SourceRef

NO_INDEXED_DOCUMENTS_REPLY = (
    "No indexed documents are available yet. Upload and index files in the "
    "knowledge base, then ask your question again."
)

NO_RETRIEVAL_CONTEXT_REPLY = (
    "I could not find relevant excerpts in your documents for this question. "
    "Try rephrasing, upload more files, or re-index existing documents if they "
    "were added before the vector store was enabled."
)

SYSTEM_PROMPT = (
    "You are Knowforge, an assistant that answers using only the provided "
    "company document excerpts. If the excerpts do not contain enough "
    "information, say you do not know and suggest uploading or checking "
    "relevant files. Be concise and factual."
)

_llama_index_configured = False


def _configure_llama_index() -> None:
    global _llama_index_configured
    if _llama_index_configured:
        return
    Settings.embed_model = OpenAIEmbedding(
        model=Config.EMBEDDING_MODEL,
        api_key=Config.OPENAI_API_KEY,
    )
    Settings.llm = OpenAI(
        model=Config.CHAT_MODEL,
        api_key=Config.OPENAI_API_KEY,
    )
    _llama_index_configured = True


def _build_memory(prior_messages: list[Message]) -> ChatMemoryBuffer:
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
    for message in prior_messages:
        if message.role == MessageRole.USER:
            memory.put(ChatMessage(role=LlamaMessageRole.USER, content=message.content))
        elif message.role == MessageRole.ASSISTANT:
            memory.put(
                ChatMessage(
                    role=LlamaMessageRole.ASSISTANT,
                    content=message.content,
                )
            )
    return memory


def _sources_from_nodes(nodes: list[NodeWithScore]) -> list[SourceRef]:
    sources: list[SourceRef] = []
    seen_chunk_ids: set[str] = set()
    for node_with_score in nodes:
        metadata = node_with_score.node.metadata
        chunk_id = metadata.get("chunk_id")
        document_id = metadata.get("document_id")
        if not chunk_id or not document_id:
            continue
        if chunk_id in seen_chunk_ids:
            continue
        seen_chunk_ids.add(chunk_id)
        quoted = node_with_score.node.get_content()
        sources.append(
            SourceRef(
                document_id=UUID(document_id),
                chunk_id=UUID(chunk_id),
                score=node_with_score.score,
                quoted_text=quoted[:2000] if quoted else None,
            )
        )
    return sources


def generate_chat_reply(
    db: Session,
    user_id: UUID,
    chat: Chat,
    user_message: str,
) -> ChatReply:
    if not db_user_has_indexed_chunks(db, user_id):
        return ChatReply(content=NO_INDEXED_DOCUMENTS_REPLY, sources=[])

    _configure_llama_index()

    prior = sorted(chat.messages, key=lambda message: message.created_at)

    retriever = create_user_retriever(user_id)

    chat_engine = ContextChatEngine.from_defaults(
        retriever=retriever,
        memory=_build_memory(prior),
        system_prompt=SYSTEM_PROMPT,
    )

    response = chat_engine.chat(user_message)

    source_nodes = list(response.source_nodes) if response.source_nodes else []

    if not source_nodes:
        return ChatReply(content=NO_RETRIEVAL_CONTEXT_REPLY, sources=[])

    content = str(response.response).strip()

    if not content or content == "Empty Response":
        return ChatReply(
            content=NO_RETRIEVAL_CONTEXT_REPLY,
            sources=_sources_from_nodes(source_nodes),
        )

    return ChatReply(
        content=content,
        sources=_sources_from_nodes(source_nodes),
    )

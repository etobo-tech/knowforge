from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.schema import NodeWithScore

from db.models import Message
from rag.query.memory import build_memory
from rag.query.prompts import SYSTEM_PROMPT


def generate_text_reply(
    *,
    user_message: str,
    prior_messages: list[Message],
    retriever: BaseRetriever,
) -> tuple[str, list[NodeWithScore]]:
    chat_engine = ContextChatEngine.from_defaults(
        retriever=retriever,
        memory=build_memory(prior_messages),
        system_prompt=SYSTEM_PROMPT,
    )
    response = chat_engine.chat(user_message)
    source_nodes = list(response.source_nodes) if response.source_nodes else []
    content = str(response.response).strip()
    return content, source_nodes

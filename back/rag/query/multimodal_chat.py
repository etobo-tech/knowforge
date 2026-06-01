from llama_index.core import Settings
from llama_index.core.llms import (
    ChatMessage,
    ImageBlock,
    LLM,
    MessageRole as LlamaMessageRole,
    TextBlock,
)
from llama_index.core.schema import NodeWithScore

from db.models import Message
from rag.config import Config
from rag.query.memory import prior_chat_messages
from rag.query.prompts import SYSTEM_PROMPT
from rag.query.sources import is_image_node
from rag.s3 import presigned_inline_url


def _split_text_and_image_nodes(
    source_nodes: list[NodeWithScore],
) -> tuple[list[NodeWithScore], list[NodeWithScore]]:
    text_nodes = [node for node in source_nodes if not is_image_node(node)]
    image_nodes = [node for node in source_nodes if is_image_node(node)]
    return text_nodes, image_nodes


def _text_context_lines(text_nodes: list[NodeWithScore]) -> list[str]:
    return [
        f"[Text excerpt {index}]\n{node_with_score.node.get_content()}"
        for index, node_with_score in enumerate(text_nodes, start=1)
    ]


def _image_context_and_blocks(
    image_nodes: list[NodeWithScore],
) -> tuple[list[str], list[ImageBlock]]:
    context_lines: list[str] = []
    image_blocks: list[ImageBlock] = []

    for index, node_with_score in enumerate(image_nodes, start=1):
        metadata = node_with_score.node.metadata
        filename = metadata.get("filename", "image")
        s3_key = metadata.get("s3_key")
        description = node_with_score.node.get_content()
        context_lines.append(
            f"[Image {index}: {filename}]\nSearch description: {description}"
        )
        if s3_key:
            image_blocks.append(
                ImageBlock(
                    url=presigned_inline_url(s3_key),
                    image_mimetype=metadata.get("mime_type"),
                    detail=Config.CHAT_IMAGE_DETAIL,
                )
            )

    return context_lines, image_blocks


def _multimodal_user_blocks(
    *,
    user_message: str,
    context_lines: list[str],
    image_blocks: list[ImageBlock],
) -> list[TextBlock | ImageBlock]:
    context_text = "\n\n".join(context_lines)
    return [
        TextBlock(
            text=(
                f"{SYSTEM_PROMPT}\n\n"
                f"Document context:\n{context_text}\n\n"
                f"User question: {user_message}"
            )
        ),
        *image_blocks,
    ]


def _configured_llm() -> LLM:
    llm = Settings.llm
    if llm is None:
        raise RuntimeError("Chat model is not configured")
    return llm


def generate_multimodal_reply(
    *,
    user_message: str,
    prior_messages: list[Message],
    source_nodes: list[NodeWithScore],
) -> str:
    text_nodes, image_nodes = _split_text_and_image_nodes(source_nodes)
    context_lines = _text_context_lines(text_nodes)
    image_context_lines, image_blocks = _image_context_and_blocks(image_nodes)
    user_blocks = _multimodal_user_blocks(
        user_message=user_message,
        context_lines=[*context_lines, *image_context_lines],
        image_blocks=image_blocks,
    )

    response = _configured_llm().chat(
        messages=[
            *prior_chat_messages(prior_messages),
            ChatMessage(role=LlamaMessageRole.USER, blocks=user_blocks),
        ]
    )
    return str(response.message.content).strip()

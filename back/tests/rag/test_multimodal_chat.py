from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from llama_index.core.schema import NodeWithScore, TextNode

from db.models import Message, MessageRole
from rag.config import Config
from rag.query import multimodal_chat


def _image_node(*, s3_key: str | None = "uploads/chart.png") -> NodeWithScore:
    return NodeWithScore(
        node=TextNode(
            text="Revenue chart description",
            metadata={
                "content_kind": Config.CONTENT_KIND_IMAGE,
                "filename": "chart.png",
                "mime_type": "image/png",
                "s3_key": s3_key,
            },
        ),
        score=0.9,
    )


def test_split_text_and_image_nodes() -> None:
    text_node = NodeWithScore(
        node=TextNode(
            text="Policy text",
            metadata={"content_kind": Config.CONTENT_KIND_TEXT},
        ),
        score=0.5,
    )
    image_node = _image_node()

    text_nodes, image_nodes = multimodal_chat._split_text_and_image_nodes(
        [text_node, image_node]
    )

    assert len(text_nodes) == 1
    assert len(image_nodes) == 1


def test_image_context_and_blocks_without_s3_key() -> None:
    lines, blocks = multimodal_chat._image_context_and_blocks(
        [_image_node(s3_key=None)]
    )

    assert "chart.png" in lines[0]
    assert blocks == []


def test_image_context_and_blocks_with_presigned_url(monkeypatch) -> None:
    monkeypatch.setattr(
        multimodal_chat,
        "presigned_inline_url",
        lambda s3_key: f"https://example.test/{s3_key}",
    )

    lines, blocks = multimodal_chat._image_context_and_blocks([_image_node()])

    assert str(blocks[0].url) == "https://example.test/uploads/chart.png"
    assert "Revenue chart" in lines[0]


def test_generate_multimodal_reply(monkeypatch) -> None:
    class FakeLLM:
        def chat(self, messages):
            return SimpleNamespace(message=SimpleNamespace(content="  Chart answer  "))

    monkeypatch.setattr(
        multimodal_chat,
        "presigned_inline_url",
        lambda s3_key: f"https://cdn.test/{s3_key}",
    )
    monkeypatch.setattr(multimodal_chat, "_configured_llm", lambda: FakeLLM())

    prior = [
        Message(
            role=MessageRole.USER,
            content="Earlier",
            created_at=datetime.now(timezone.utc),
        ),
    ]
    content = multimodal_chat.generate_multimodal_reply(
        user_message="What does the chart show?",
        prior_messages=prior,
        source_nodes=[_image_node()],
    )

    assert content == "Chart answer"

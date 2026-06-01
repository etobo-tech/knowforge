from datetime import datetime, timezone
from uuid import uuid4

from api.schemas.chats import ChatDetailResponse, MessageResponse, MessageSourceResponse
from db.models import Chat, Message, MessageRole, MessageSource


def test_chat_detail_response_from_orm() -> None:
    chat_id = uuid4()
    now = datetime.now(timezone.utc)
    chat = Chat(
        id=chat_id,
        user_id=uuid4(),
        title="Test",
        created_at=now,
        updated_at=now,
    )
    chat.messages = [
        Message(
            id=uuid4(),
            chat_id=chat_id,
            role=MessageRole.USER,
            content="Hi",
            created_at=now,
        ),
    ]

    response = ChatDetailResponse.model_validate(chat)

    assert response.id == chat_id
    assert len(response.messages) == 1
    assert response.messages[0].role == MessageRole.USER.value


def test_message_response_defaults_sources_to_empty() -> None:
    now = datetime.now(timezone.utc)
    message = Message(
        id=uuid4(),
        chat_id=uuid4(),
        role=MessageRole.ASSISTANT,
        content="Answer",
        created_at=now,
    )

    response = MessageResponse.model_validate(message)

    assert response.sources == []


def test_message_source_response_reads_metadata_fields() -> None:
    source = MessageSource(
        id=uuid4(),
        message_id=uuid4(),
        document_id=uuid4(),
        chunk_id=uuid4(),
        score=0.88,
        quoted_text="Excerpt",
        metadata_={
            "content_kind": "image",
            "filename": "diagram.png",
            "mime_type": "image/png",
        },
    )

    response = MessageSourceResponse.model_validate(source)

    assert response.content_kind == "image"
    assert response.filename == "diagram.png"
    assert response.mime_type == "image/png"

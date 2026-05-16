from datetime import datetime, timezone
from uuid import uuid4

from api.schemas.chats import ChatDetailResponse, MessageResponse
from db.models import Chat, Message, MessageRole


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

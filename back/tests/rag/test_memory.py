from datetime import datetime, timezone

from db.models import Message, MessageRole
from rag.query.memory import prior_chat_messages


def test_prior_chat_messages_excludes_system_role() -> None:
    messages = [
        Message(
            role=MessageRole.USER,
            content="Hi",
            created_at=datetime.now(timezone.utc),
        ),
        Message(
            role=MessageRole.SYSTEM,
            content="Hidden",
            created_at=datetime.now(timezone.utc),
        ),
    ]

    chat_messages = prior_chat_messages(messages)

    assert len(chat_messages) == 1
    assert chat_messages[0].content == "Hi"

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from db.models import Message
from db.repositories.chats import (
    db_append_assistant_with_sources,
    db_append_message,
    db_create_chat,
    db_get_chat_for_user,
)
from db.models import MessageRole
from tests.helpers.constants import DEV_USER_ID


def seed_chat_with_turns(
    db_session: Session,
    turns: list[tuple[str, str]],
):
    chat = db_create_chat(db_session, DEV_USER_ID, title="Delete test")
    messages: list[Message] = []
    base_time = datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc)

    for index, (user_content, assistant_content) in enumerate(turns):
        user_message = db_append_message(
            db_session,
            chat,
            MessageRole.USER,
            user_content,
        )
        user_message.created_at = base_time + timedelta(seconds=index * 10)
        assistant_message = db_append_assistant_with_sources(
            db_session,
            chat,
            assistant_content,
            [],
        )
        assistant_message.created_at = base_time + timedelta(seconds=index * 10 + 1)
        messages.extend([user_message, assistant_message])

    db_session.commit()
    loaded = db_get_chat_for_user(db_session, DEV_USER_ID, chat.id)
    return loaded, messages

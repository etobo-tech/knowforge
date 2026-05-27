from db.models import MessageRole
from db.repositories.chats import (
    db_append_message,
    db_create_chat,
    db_get_chat_for_user,
    db_list_chats_for_user,
    db_update_chat_title,
)
from sqlalchemy.orm import Session
from tests.helpers.constants import DEV_USER_ID


def test_chat_repository_lifecycle(db_session: Session) -> None:
    chat = db_create_chat(db_session, DEV_USER_ID, title="Support")
    db_append_message(
        db_session,
        chat,
        MessageRole.USER,
        "Hello",
    )

    listed = db_list_chats_for_user(db_session, DEV_USER_ID)
    loaded = db_get_chat_for_user(db_session, DEV_USER_ID, chat.id)

    assert len(listed) == 1
    assert len(loaded.messages) == 1
    assert loaded.messages[0].role == MessageRole.USER

    updated = db_update_chat_title(db_session, loaded, "Renamed")
    assert updated.title == "Renamed"

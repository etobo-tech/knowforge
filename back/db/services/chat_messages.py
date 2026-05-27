from uuid import UUID

from sqlalchemy.orm import Session

from db.models import Chat, MessageRole
from db.repositories.chats import (
    db_append_assistant_with_sources,
    db_append_message,
    db_get_chat_for_user,
    db_reload_chat_for_user,
)
from rag.query.service import generate_chat_reply


def process_incoming_message(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    user_message: str,
) -> Chat:
    chat = db_get_chat_for_user(db, user_id, chat_id)
    reply = generate_chat_reply(db, user_id, chat, user_message)
    try:
        db_append_message(db, chat, MessageRole.USER, user_message)
        db_append_assistant_with_sources(db, chat, reply.content, reply.sources)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return db_reload_chat_for_user(db, user_id, chat_id)

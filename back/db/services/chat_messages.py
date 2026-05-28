from uuid import UUID

from sqlalchemy.orm import Session

from db.models import Chat, MessageRole, Message
from db.repositories.chats import (
    db_append_assistant_with_sources,
    db_append_message,
    db_get_chat_for_user,
    db_reload_chat_for_user,
)
from rag.query.service import generate_chat_reply
from fastapi import HTTPException
from fastapi import status
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


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


def _get_msg_range_to_delete(
    db: Session, chat: Chat, message_id: UUID
) -> list[Message]:
    target_message = next(
        (message for message in chat.messages if message.id == message_id), None
    )

    if not target_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found",
        )
    if target_message.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message {message_id} is not a user message",
        )

    return [
        message
        for message in chat.messages
        if message.created_at >= target_message.created_at
    ]


def process_message_deletion(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    message_id: UUID,
) -> None:
    chat = db_get_chat_for_user(db, user_id, chat_id)

    subsequent_messages = _get_msg_range_to_delete(db, chat, message_id)
    try:
        for message in subsequent_messages:
            db.delete(message)
        chat.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        logger.exception(f"Failed to delete message {message_id}: {e}")
        db.rollback()
        raise

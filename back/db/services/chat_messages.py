from typing import NamedTuple
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
from api.schemas.chats import MessageUpdateRequest
from fastapi import HTTPException
from fastapi import status
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TargetAndNextMessages(NamedTuple):
    target_message: Message
    next_messages: list[Message]


def process_incoming_message(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    user_message: str,
) -> Chat:
    chat = db_get_chat_for_user(db, user_id, chat_id)

    prior_messages = sorted(chat.messages, key=lambda message: message.created_at)

    reply = generate_chat_reply(db, user_id, user_message, prior_messages)
    try:
        db_append_message(db, chat, MessageRole.USER, user_message)
        db_append_assistant_with_sources(db, chat, reply.content, reply.sources)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return db_reload_chat_for_user(db, user_id, chat_id)


def _message_order_key(message: Message) -> tuple[datetime, str]:
    return (message.created_at, str(message.id))


def _messages_before_target(chat: Chat, target: Message) -> list[Message]:
    return [
        message for message in chat.messages if message.created_at < target.created_at
    ]


def _messages_after_target(chat: Chat, target: Message) -> list[Message]:
    return [
        message
        for message in chat.messages
        if message.id != target.id
        and (
            message.created_at > target.created_at
            or message.created_at == target.created_at
        )
    ]


def _get_target_and_next_messages(
    chat: Chat, message_id: UUID
) -> TargetAndNextMessages:
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

    return TargetAndNextMessages(
        target_message=target_message,
        next_messages=_messages_after_target(chat, target_message),
    )


def process_message_deletion(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    message_id: UUID,
) -> None:
    chat = db_get_chat_for_user(db, user_id, chat_id)

    target_and_next = _get_target_and_next_messages(chat, message_id)
    try:
        db.delete(target_and_next.target_message)

        for message in target_and_next.next_messages:
            db.delete(message)

        chat.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        logger.exception(f"Failed to delete message {message_id}: {e}")
        db.rollback()
        raise


def process_message_update(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    message_id: UUID,
    body: MessageUpdateRequest,
) -> Chat:
    edited_content = body.content.strip()

    if edited_content == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty",
        )

    chat = db_get_chat_for_user(db, user_id, chat_id)

    target_and_next = _get_target_and_next_messages(chat, message_id)

    try:
        for message_to_delete in target_and_next.next_messages:
            db.delete(message_to_delete)
        target_and_next.target_message.content = edited_content
        chat.updated_at = datetime.now(timezone.utc)
        db.flush()

        prior_messages = sorted(
            _messages_before_target(chat, target_and_next.target_message),
            key=_message_order_key,
        )

        reply = generate_chat_reply(db, user_id, edited_content, prior_messages)
        db_append_assistant_with_sources(db, chat, reply.content, reply.sources)
        db.commit()
        return db_reload_chat_for_user(db, user_id, chat_id)
    except Exception as e:
        logger.exception(f"Failed to update message {message_id}: {e}")
        db.rollback()
        raise

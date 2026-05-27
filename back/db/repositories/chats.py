from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Query, Session, joinedload

from db.models import Chat, Message, MessageRole, MessageSource
from rag.query.types import SourceRef


def db_create_chat(
    db: Session,
    user_id: UUID,
    *,
    title: str = "New chat",
) -> Chat:
    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def db_list_chats_for_user(db: Session, user_id: UUID) -> list[Chat]:
    return (
        db.query(Chat)
        .filter(Chat.user_id == user_id)
        .order_by(Chat.updated_at.desc())
        .all()
    )


def _chat_with_messages_query(db: Session) -> Query[Chat]:
    return db.query(Chat).options(joinedload(Chat.messages).joinedload(Message.sources))


def db_get_chat_for_user(db: Session, user_id: UUID, chat_id: UUID) -> Chat:
    chat = (
        _chat_with_messages_query(db)
        .filter(Chat.id == chat_id, Chat.user_id == user_id)
        .first()
    )
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )
    return chat


def db_reload_chat_for_user(db: Session, user_id: UUID, chat_id: UUID) -> Chat:
    return (
        _chat_with_messages_query(db)
        .filter(Chat.id == chat_id, Chat.user_id == user_id)
        .one()
    )


def db_update_chat_title(db: Session, chat: Chat, title: str) -> Chat:
    chat.title = title
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(chat)
    return chat


def db_append_message(
    db: Session,
    chat: Chat,
    role: MessageRole,
    content: str,
) -> Message:
    message = Message(chat_id=chat.id, role=role, content=content)
    db.add(message)
    chat.updated_at = datetime.now(timezone.utc)
    db.flush()
    db.refresh(message)
    return message


def db_append_assistant_with_sources(
    db: Session,
    chat: Chat,
    content: str,
    sources: list[SourceRef],
) -> Message:
    """Stage an assistant message + sources. Caller is responsible for commit/rollback."""
    message = Message(
        chat_id=chat.id,
        role=MessageRole.ASSISTANT,
        content=content,
    )
    db.add(message)
    db.flush()

    for source in sources:
        db.add(
            MessageSource(
                message_id=message.id,
                document_id=source.document_id,
                chunk_id=source.chunk_id,
                score=source.score,
                quoted_text=source.quoted_text,
            )
        )

    chat.updated_at = datetime.now(timezone.utc)
    db.flush()
    db.refresh(message)
    return message

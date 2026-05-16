from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from db.models import Chat, Message, MessageRole


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


def db_get_chat_for_user(db: Session, user_id: UUID, chat_id: UUID) -> Chat | None:
    return (
        db.query(Chat)
        .options(joinedload(Chat.messages))
        .filter(Chat.id == chat_id, Chat.user_id == user_id)
        .first()
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
    db.commit()
    db.refresh(message)
    return message

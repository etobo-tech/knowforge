from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.schemas.chats import (
    ChatCreateRequest,
    ChatDetailResponse,
    ChatSummaryResponse,
    ChatUpdateRequest,
    MessageCreateRequest,
    MessageResponse,
)
from db.models import Chat, MessageRole
from db.repositories.chats import (
    db_append_message,
    db_create_chat,
    db_get_chat_for_user,
    db_list_chats_for_user,
    db_update_chat_title,
)
from db.session import get_db

DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

router = APIRouter(prefix="/chats", tags=["chats"])


def _messages_sorted(chat: Chat) -> list[MessageResponse]:
    ordered = sorted(chat.messages, key=lambda m: m.created_at)
    return [MessageResponse.model_validate(m) for m in ordered]


def _chat_detail(chat: Chat) -> ChatDetailResponse:
    return ChatDetailResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=_messages_sorted(chat),
    )


@router.post("", response_model=ChatDetailResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    body: ChatCreateRequest | None = None,
    db: Session = Depends(get_db),
) -> ChatDetailResponse:
    title = (body.title if body and body.title else None) or "New chat"
    chat = db_create_chat(db, DEV_USER_ID, title=title)
    return _chat_detail(chat)


@router.get("", response_model=list[ChatSummaryResponse])
def list_chats(db: Session = Depends(get_db)) -> list[ChatSummaryResponse]:
    chats = db_list_chats_for_user(db, DEV_USER_ID)
    return [ChatSummaryResponse.model_validate(c) for c in chats]


@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat(chat_id: UUID, db: Session = Depends(get_db)) -> ChatDetailResponse:
    chat = db_get_chat_for_user(db, DEV_USER_ID, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return _chat_detail(chat)


@router.patch("/{chat_id}", response_model=ChatDetailResponse)
def update_chat(
    chat_id: UUID,
    body: ChatUpdateRequest,
    db: Session = Depends(get_db),
) -> ChatDetailResponse:
    chat = db_get_chat_for_user(db, DEV_USER_ID, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    chat = db_update_chat_title(db, chat, body.title.strip())
    return _chat_detail(chat)


@router.post("/{chat_id}/messages", response_model=ChatDetailResponse)
def append_message(
    chat_id: UUID,
    body: MessageCreateRequest,
    db: Session = Depends(get_db),
) -> ChatDetailResponse:
    chat = db_get_chat_for_user(db, DEV_USER_ID, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    content = body.content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty",
        )

    db_append_message(db, chat, MessageRole.USER, content)
    chat = db_get_chat_for_user(db, DEV_USER_ID, chat_id)
    assert chat is not None
    return _chat_detail(chat)

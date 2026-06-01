from uuid import uuid4

from db.models import MessageRole
from db.repositories.chats import (
    db_append_assistant_with_sources,
    db_append_message,
    db_create_chat,
    db_get_chat_for_user,
    db_list_chats_for_user,
    db_update_chat_title,
)
from rag.query.types import SourceRef
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


def test_db_append_assistant_persists_source_metadata(db_session: Session) -> None:
    chat = db_create_chat(db_session, DEV_USER_ID, title="Sources")
    document_id = uuid4()
    chunk_id = uuid4()

    message = db_append_assistant_with_sources(
        db_session,
        chat,
        "Answer",
        [
            SourceRef(
                document_id=document_id,
                chunk_id=chunk_id,
                score=0.95,
                quoted_text="snippet",
                content_kind="image",
                s3_key="users/u/doc.png",
                filename="doc.png",
                mime_type="image/png",
            ),
        ],
    )
    db_session.commit()
    db_session.refresh(message)

    assert len(message.sources) == 1
    metadata = message.sources[0].metadata_
    assert metadata is not None
    assert metadata["content_kind"] == "image"
    assert metadata["s3_key"] == "users/u/doc.png"
    assert metadata["filename"] == "doc.png"
    assert metadata["mime_type"] == "image/png"

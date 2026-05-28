from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.repositories.chats import db_get_chat_for_user
from db.services.chat_messages import process_message_deletion
from tests.helpers.chats import seed_chat_with_turns
from tests.helpers.constants import DEV_USER_ID


def test_process_message_deletion_truncates_from_target_user_message(
    db_session: Session,
) -> None:
    chat, messages = seed_chat_with_turns(
        db_session,
        [
            ("First question", "First answer"),
            ("Second question", "Second answer"),
            ("Third question", "Third answer"),
        ],
    )
    second_user_message = messages[2]

    process_message_deletion(
        db_session,
        DEV_USER_ID,
        chat.id,
        second_user_message.id,
    )

    reloaded = db_get_chat_for_user(db_session, DEV_USER_ID, chat.id)
    remaining_content = [message.content for message in reloaded.messages]

    assert remaining_content == ["First question", "First answer"]


def test_process_message_deletion_removes_entire_chat_history_from_first_turn(
    db_session: Session,
) -> None:
    chat, messages = seed_chat_with_turns(
        db_session,
        [
            ("Only question", "Only answer"),
            ("Later question", "Later answer"),
        ],
    )
    first_user_message = messages[0]

    process_message_deletion(
        db_session,
        DEV_USER_ID,
        chat.id,
        first_user_message.id,
    )

    reloaded = db_get_chat_for_user(db_session, DEV_USER_ID, chat.id)
    assert reloaded.messages == []


def test_process_message_deletion_rejects_non_user_message(
    db_session: Session,
) -> None:
    chat, messages = seed_chat_with_turns(
        db_session,
        [("Question", "Answer")],
    )
    assistant_message = messages[1]

    with pytest.raises(HTTPException) as exc_info:
        process_message_deletion(
            db_session,
            DEV_USER_ID,
            chat.id,
            assistant_message.id,
        )

    assert exc_info.value.status_code == 400


def test_process_message_deletion_returns_404_for_unknown_message(
    db_session: Session,
) -> None:
    chat, _ = seed_chat_with_turns(
        db_session,
        [("Question", "Answer")],
    )

    with pytest.raises(HTTPException) as exc_info:
        process_message_deletion(
            db_session,
            DEV_USER_ID,
            chat.id,
            uuid4(),
        )

    assert exc_info.value.status_code == 404


def test_process_message_deletion_returns_404_for_unknown_chat(
    db_session: Session,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        process_message_deletion(
            db_session,
            DEV_USER_ID,
            uuid4(),
            uuid4(),
        )

    assert exc_info.value.status_code == 404

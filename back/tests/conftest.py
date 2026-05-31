import os
from collections.abc import Generator
from typing import Any

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite://"

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["OPENAI_API_KEY"] = "test-openai-key"

from db import models as db_models  # noqa: E402
from db.base import Base  # noqa: E402
from rag.config import Config  # noqa: E402
from rag.s3 import get_s3_client  # noqa: E402
from tests.helpers.embeddings import deterministic_embeddings  # noqa: E402
from tests.helpers.vector_store import patch_vector_store, reset_fake_vector_store  # noqa: E402

db_models.DocumentChunk.__table__.c.embedding.type = JSON()
db_models.MessageSource.__table__.c.metadata.type = JSON()


@pytest.fixture
def engine() -> Generator[Any, None, None]:
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db_session(engine: Any) -> Generator[Session, None, None]:
    session = sessionmaker(bind=engine)()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True)
def fake_vector_store(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_fake_vector_store()
    patch_vector_store(monkeypatch)


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "rag.indexing.embed.embed_texts",
        deterministic_embeddings,
    )
    monkeypatch.setattr(
        "rag.indexing.text.embed_texts",
        deterministic_embeddings,
    )
    monkeypatch.setattr(
        "rag.indexing.image.embed_texts",
        deterministic_embeddings,
    )


@pytest.fixture(autouse=True)
def fake_image_vision(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_description(content: bytes, mime_type: str) -> str:
        return f"Search description for {mime_type} ({len(content)} bytes)"

    monkeypatch.setattr(
        "rag.indexing.image.generate_image_search_description",
        _fake_description,
    )


@pytest.fixture(autouse=True)
def fake_chat_reply(monkeypatch: pytest.MonkeyPatch) -> None:
    from rag.query.types import ChatReply

    def _fake_generate_chat_reply(
        db, user_id, user_message: str, prior_messages
    ) -> ChatReply:
        return ChatReply(
            content=f"Test reply to: {user_message}",
            sources=[],
        )

    monkeypatch.setattr(
        "db.services.chat_messages.generate_chat_reply",
        _fake_generate_chat_reply,
    )


@pytest.fixture
def s3_mock() -> Generator[None, None, None]:
    get_s3_client.cache_clear()
    with mock_aws():
        client = boto3.client("s3", region_name=Config.S3_REGION)
        client.create_bucket(Bucket=Config.S3_BUCKET)
        yield
    get_s3_client.cache_clear()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    from api.main import app
    from db.session import get_db

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

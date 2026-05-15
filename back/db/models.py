import enum
import uuid as _uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from db.base import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_user_content", "user_id", "content_hash", unique=True),
    )

    id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    user_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False, length=20),
        nullable=False,
        default=DocumentStatus.UPLOADING,
        index=True,
    )
    chunks_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    sources: Mapped[list["MessageSource"]] = relationship(back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_chunks_document_index", "document_id", "chunk_index", unique=True),
    )

    id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    document_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(1536), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    document: Mapped["Document"] = relationship(back_populates="chunks")
    sources: Mapped[list["MessageSource"]] = relationship(back_populates="chunk")


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    user_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="New chat")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    chat_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, native_enum=False, length=20), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    sources: Mapped[list["MessageSource"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class MessageSource(Base):
    __tablename__ = "message_sources"

    id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    message_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quoted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    message: Mapped["Message"] = relationship(back_populates="sources")
    document: Mapped["Document"] = relationship(back_populates="sources")
    chunk: Mapped["DocumentChunk"] = relationship(back_populates="sources")

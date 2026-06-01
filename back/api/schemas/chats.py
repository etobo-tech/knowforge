from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be empty")
        return stripped


class ChatUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class MessageUpdateRequest(BaseModel):
    content: str = Field(min_length=1)


class MessageSourceResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_id: UUID
    score: float | None
    quoted_text: str | None
    content_kind: str | None = None
    filename: str | None = None
    mime_type: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "MessageSourceResponse":
        base = super().model_validate(obj, **kwargs)
        metadata = getattr(obj, "metadata_", None) or {}
        if not isinstance(metadata, dict):
            return base
        return cls(
            id=base.id,
            document_id=base.document_id,
            chunk_id=base.chunk_id,
            score=base.score,
            quoted_text=base.quoted_text,
            content_kind=metadata.get("content_kind"),
            filename=metadata.get("filename"),
            mime_type=metadata.get("mime_type"),
        )


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    sources: list[MessageSourceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ChatSummaryResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

    model_config = ConfigDict(from_attributes=True)

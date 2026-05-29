from datetime import datetime
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

    model_config = ConfigDict(from_attributes=True)


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

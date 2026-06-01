from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SourceRef:
    document_id: UUID
    chunk_id: UUID
    score: float | None
    quoted_text: str | None
    content_kind: str | None = None
    s3_key: str | None = None
    filename: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True)
class ChatReply:
    content: str
    sources: list[SourceRef]

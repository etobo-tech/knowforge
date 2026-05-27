from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SourceRef:
    document_id: UUID
    chunk_id: UUID
    score: float | None
    quoted_text: str | None


@dataclass(frozen=True)
class ChatReply:
    content: str
    sources: list[SourceRef]

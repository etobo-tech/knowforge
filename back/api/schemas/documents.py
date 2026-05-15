from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    status: str
    content_hash: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


class Citation(BaseModel):
    file_id: str
    chunk_id: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]

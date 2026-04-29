from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.local_chat_rag import answer_question

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(*, request: ChatRequest) -> ChatResponse:
    return answer_question(request=request)

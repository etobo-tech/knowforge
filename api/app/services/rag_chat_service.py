from app.core.constants import CHAT_TOP_K
from app.db.models.rag import MetricEventType
from app.db.session import SessionFactory
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services.ai_embeddings import build_openai_embedding_client
from app.services.ai_llm import generate_grounded_answer
from app.services.repositories.rag_repository import RagRepository


def answer_question(*, request: ChatRequest) -> ChatResponse:
    with SessionFactory() as session:
        repository = RagRepository(session=session)
        embedding_client = build_openai_embedding_client()
        query_embedding = embedding_client.get_text_embedding(request.question)
        matches = repository.search_similar_chunks(
            workspace_id=request.workspace_id,
            query_embedding=query_embedding,
            top_k=CHAT_TOP_K,
        )

        if not matches:
            return ChatResponse(
                answer=(
                    "I do not have enough context in the uploaded files to answer that question."
                ),
                citations=[],
            )

        context_chunks = [chunk.content for chunk, _ in matches]
        answer = generate_grounded_answer(
            question=request.question,
            context_chunks=context_chunks,
        )
        citations = [
            Citation(file_id=str(chunk.document_id), chunk_id=str(chunk.id))
            for chunk, _ in matches
        ]
        repository.log_metric_event(
            workspace_id=request.workspace_id,
            event_type=MetricEventType.CHAT_ANSWERED_WITH_CITATIONS,
            payload={"citations_count": len(citations)},
        )
        session.commit()
        return ChatResponse(answer=answer, citations=citations)

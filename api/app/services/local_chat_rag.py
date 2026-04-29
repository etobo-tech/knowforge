import json
from dataclasses import dataclass

from app.core.constants import CHAT_TOP_K, LOCAL_CHUNKS_ROOT
from app.schemas.chat import ChatRequest, ChatResponse, Citation


@dataclass(frozen=True)
class ScoredChunk:
    score: int
    file_id: str
    chunk_id: str
    content: str


def _tokenize(*, text: str) -> set[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return {token for token in normalized.split() if len(token) >= 3}


def _score_text(*, text: str, tokenized_question: set[str]) -> int:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    words = set(normalized.split())
    return len(words.intersection(tokenized_question))


def _retrieve_scored_chunks(*, workspace_id: str, question: str) -> list[ScoredChunk]:
    tokenized_question = _tokenize(text=question)
    if not tokenized_question:
        return []

    chunks = _load_workspace_chunks(workspace_id=workspace_id)
    scored: list[ScoredChunk] = []
    for chunk in chunks:
        score = _score_text(
            text=chunk["content"], tokenized_question=tokenized_question
        )
        if score > 0:
            scored.append(
                ScoredChunk(
                    score=score,
                    file_id=chunk["file_id"],
                    chunk_id=chunk["chunk_id"],
                    content=chunk["content"],
                )
            )

    return sorted(scored, key=lambda item: item.score, reverse=True)


def _load_workspace_chunks(*, workspace_id: str) -> list[dict[str, str]]:
    if not LOCAL_CHUNKS_ROOT.exists():
        return []

    chunks: list[dict[str, str]] = []
    for chunks_file in LOCAL_CHUNKS_ROOT.glob("*.json"):
        payload = json.loads(chunks_file.read_text())
        if not isinstance(payload, list):
            continue
        for item in payload:
            if not isinstance(item, dict):
                continue
            if item.get("workspace_id") != workspace_id:
                continue
            file_id = item.get("file_id")
            chunk_id = item.get("chunk_id")
            content = item.get("content")
            if (
                not isinstance(file_id, str)
                or not isinstance(chunk_id, str)
                or not isinstance(content, str)
            ):
                continue
            chunks.append(
                {
                    "file_id": file_id,
                    "chunk_id": chunk_id,
                    "content": content,
                }
            )
    return chunks


def answer_question(*, request: ChatRequest) -> ChatResponse:
    scored_chunks = _retrieve_scored_chunks(
        workspace_id=request.workspace_id,
        question=request.question,
    )

    if not scored_chunks:
        return ChatResponse(
            answer=(
                "I do not have enough context in the uploaded files to answer that question."
            ),
            citations=[],
        )

    top_chunks = scored_chunks[:CHAT_TOP_K]
    answer_parts = [
        "I found relevant information in your uploaded files:",
        *[f"- {chunk.content[:220].strip()}" for chunk in top_chunks],
    ]
    citations = [
        Citation(file_id=chunk.file_id, chunk_id=chunk.chunk_id) for chunk in top_chunks
    ]
    return ChatResponse(answer="\n".join(answer_parts), citations=citations)

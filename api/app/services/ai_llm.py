from llama_index.llms.openai import OpenAI

from app.core.settings import get_app_settings


def build_openai_llm_client() -> OpenAI:
    settings = get_app_settings()
    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for answer generation.")
    return OpenAI(model=settings.openai_model, api_key=api_key, temperature=0.1)


def generate_grounded_answer(*, question: str, context_chunks: list[str]) -> str:
    llm = build_openai_llm_client()
    context_text = "\n\n".join(
        f"[Context {index + 1}]\n{chunk}" for index, chunk in enumerate(context_chunks)
    )
    prompt = (
        "You are a retrieval-augmented assistant.\n"
        "Answer only with information supported by the provided context.\n"
        "If context is insufficient, say you do not have enough context.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context_text}\n\n"
        "Answer:"
    )
    return llm.complete(prompt).text.strip()

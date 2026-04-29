from llama_index.embeddings.openai import OpenAIEmbedding

from app.core.settings import get_app_settings


def build_openai_embedding_client() -> OpenAIEmbedding:
    settings = get_app_settings()
    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for embedding generation.")
    return OpenAIEmbedding(model=settings.embedding_model, api_key=api_key)

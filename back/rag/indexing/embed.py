from llama_index.core import Settings

from rag.llama_settings import configure_llama_index


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    configure_llama_index()

    embed_model = Settings.embed_model
    if embed_model is None:
        raise RuntimeError("Embedding model is not configured")

    return embed_model.get_text_embedding_batch(texts)

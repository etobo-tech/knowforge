from openai import OpenAI

from rag.config import Config


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    response = client.embeddings.create(
        model=Config.EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]

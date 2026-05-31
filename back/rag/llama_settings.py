from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from rag.config import Config

_configured = False


def configure_llama_index() -> None:
    global _configured
    if _configured:
        return

    Settings.embed_model = OpenAIEmbedding(
        model=Config.EMBEDDING_MODEL,
        api_key=Config.OPENAI_API_KEY,
    )
    Settings.llm = OpenAI(
        model=Config.CHAT_MODEL,
        api_key=Config.OPENAI_API_KEY,
    )
    _configured = True


def get_vision_llm(*, detail: str) -> OpenAI:
    configure_llama_index()

    return OpenAI(
        model=Config.VISION_MODEL,
        api_key=Config.OPENAI_API_KEY,
        model_kwargs={"detail": detail},
    )

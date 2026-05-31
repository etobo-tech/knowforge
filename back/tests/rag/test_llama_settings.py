from llama_index.core import Settings

from rag import llama_settings


def test_configure_llama_index_is_idempotent() -> None:
    llama_settings._configured = False
    llama_settings.configure_llama_index()
    embed_model = Settings.embed_model
    llama_settings.configure_llama_index()
    assert Settings.embed_model is embed_model


def test_get_vision_llm_returns_openai_llm() -> None:
    llm = llama_settings.get_vision_llm(detail="low")
    assert llm is not None

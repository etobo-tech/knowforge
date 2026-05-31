from llama_index.core import Settings

from rag.llama_settings import configure_llama_index


def test_configure_llama_index_sets_embed_and_chat_models() -> None:
    configure_llama_index()

    assert Settings.embed_model is not None
    assert Settings.llm is not None

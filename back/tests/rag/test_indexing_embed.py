from rag.indexing.embed import embed_texts


class _FakeEmbedModel:
    def get_text_embedding_batch(self, texts: list[str]) -> list[list[float]]:
        return [[float(index)] * 4 for index, _ in enumerate(texts)]


def test_embed_texts_returns_empty_for_no_input() -> None:
    assert embed_texts([]) == []


def test_embed_texts_uses_configured_embed_model(monkeypatch) -> None:
    import rag.indexing.embed as embed_module

    class _FakeSettings:
        embed_model = _FakeEmbedModel()

    monkeypatch.setattr(
        embed_module,
        "configure_llama_index",
        lambda: None,
    )
    monkeypatch.setattr(embed_module, "Settings", _FakeSettings())

    result = embed_texts(["alpha", "beta"])

    assert len(result) == 2
    assert result[0][0] == 0.0

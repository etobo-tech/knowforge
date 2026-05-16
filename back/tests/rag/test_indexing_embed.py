from rag.indexing.embed import embed_texts


def test_embed_texts_returns_empty_for_no_input() -> None:
    assert embed_texts([]) == []

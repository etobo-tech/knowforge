from rag.indexing.chunk import chunk_text


def test_chunk_text_splits_long_document() -> None:
    text = "Sentence one. " * 2000

    chunks = chunk_text(text)

    assert len(chunks) >= 2
    assert all(chunk.strip() for chunk in chunks)


def test_chunk_text_returns_single_chunk_for_short_text() -> None:
    chunks = chunk_text("hello")

    assert chunks == ["hello"]

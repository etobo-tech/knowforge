from functools import lru_cache

from llama_index.core.node_parser import SentenceSplitter

from rag.config import Config


@lru_cache
def _get_splitter() -> SentenceSplitter:
    return SentenceSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )


def chunk_text(text: str) -> list[str]:
    stripped = text.strip()
    chunks = _get_splitter().split_text(stripped)

    if not chunks:
        raise ValueError("Document has no extractable text")

    return chunks

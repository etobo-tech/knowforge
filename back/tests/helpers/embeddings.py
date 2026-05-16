from tests.helpers.constants import EMBEDDING_DIMENSION


def deterministic_embeddings(texts: list[str]) -> list[list[float]]:
    return [
        [(index + 1) / (EMBEDDING_DIMENSION + 1)] * EMBEDDING_DIMENSION
        for index, _ in enumerate(texts)
    ]

from uuid import UUID

from llama_index.core import VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle

from rag.config import Config
from rag.vector_store import (
    get_pg_image_vector_store,
    get_pg_vector_store,
    user_metadata_filters,
)


class FusedVectorRetriever(BaseRetriever):
    """Retrieve from text and image PGVector stores, merge by score."""

    def __init__(
        self,
        *,
        retrievers: list[BaseRetriever],
        similarity_top_k: int,
    ) -> None:
        self._retrievers = retrievers
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        merged: dict[str, NodeWithScore] = {}
        for retriever in self._retrievers:
            for node_with_score in retriever.retrieve(query_bundle):
                node_id = node_with_score.node.node_id
                existing = merged.get(node_id)
                if existing is None or _score_value(
                    node_with_score.score
                ) > _score_value(existing.score):
                    merged[node_id] = node_with_score

        ranked = sorted(
            merged.values(),
            key=lambda item: _score_value(item.score),
            reverse=True,
        )
        return ranked[: self._similarity_top_k]


def _score_value(score: float | None) -> float:
    return score if score is not None else float("-inf")


def create_user_retriever(user_id: UUID) -> BaseRetriever:
    user_filters = user_metadata_filters(user_id)

    text_index = VectorStoreIndex.from_vector_store(get_pg_vector_store())
    image_index = VectorStoreIndex.from_vector_store(get_pg_image_vector_store())

    text_retriever = text_index.as_retriever(
        similarity_top_k=Config.TOP_K,
        filters=user_filters,
    )
    image_retriever = image_index.as_retriever(
        similarity_top_k=Config.TOP_K,
        filters=user_filters,
    )

    return FusedVectorRetriever(
        retrievers=[text_retriever, image_retriever],
        similarity_top_k=Config.TOP_K,
    )

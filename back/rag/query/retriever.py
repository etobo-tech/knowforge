from uuid import UUID

from llama_index.core import VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever

from rag.config import Config
from rag.vector_store import get_pg_vector_store, user_metadata_filters


def create_user_retriever(user_id: UUID) -> BaseRetriever:
    store = get_pg_vector_store()

    index = VectorStoreIndex.from_vector_store(store)
    user_filters = user_metadata_filters(user_id)
    return index.as_retriever(similarity_top_k=Config.TOP_K, filters=user_filters)

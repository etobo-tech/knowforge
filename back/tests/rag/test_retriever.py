from uuid import uuid4

from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

from rag.query.retriever import FusedVectorRetriever, _score_value, create_user_retriever


class _StubRetriever:
    def __init__(self, nodes: list[NodeWithScore]) -> None:
        self._nodes = nodes

    def retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        return self._nodes


def test_score_value_treats_none_as_negative_infinity() -> None:
    assert _score_value(None) == float("-inf")
    assert _score_value(0.5) == 0.5


def test_fused_retriever_merges_by_best_score() -> None:
    shared_id = "shared-node"
    low = NodeWithScore(
        node=TextNode(text="low", id_=shared_id),
        score=0.2,
    )
    high = NodeWithScore(
        node=TextNode(text="high", id_=shared_id),
        score=0.9,
    )
    other = NodeWithScore(
        node=TextNode(text="other", id_="other-node"),
        score=0.5,
    )

    retriever = FusedVectorRetriever(
        retrievers=[
            _StubRetriever([low, other]),
            _StubRetriever([high]),
        ],
        similarity_top_k=2,
    )

    results = retriever._retrieve(QueryBundle(query_str="query"))

    assert len(results) == 2
    assert results[0].score == 0.9
    assert results[0].node.node_id == shared_id


def test_create_user_retriever_builds_fused_retriever(monkeypatch) -> None:
    class FakeIndex:
        def __init__(self, label: str) -> None:
            self.label = label

        def as_retriever(self, *, similarity_top_k, filters):
            return _StubRetriever(
                [
                    NodeWithScore(
                        node=TextNode(text=self.label, id_=self.label),
                        score=0.1,
                    )
                ]
            )

    monkeypatch.setattr(
        "rag.query.retriever.VectorStoreIndex.from_vector_store",
        lambda store: FakeIndex("text" if store is text_store else "image"),
    )
    text_store = object()
    image_store = object()
    monkeypatch.setattr(
        "rag.query.retriever.get_pg_vector_store",
        lambda: text_store,
    )
    monkeypatch.setattr(
        "rag.query.retriever.get_pg_image_vector_store",
        lambda: image_store,
    )

    retriever = create_user_retriever(uuid4())

    assert isinstance(retriever, FusedVectorRetriever)
    results = retriever.retrieve(QueryBundle(query_str="hello"))
    assert len(results) == 2

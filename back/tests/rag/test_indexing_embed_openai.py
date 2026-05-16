from types import SimpleNamespace

from rag.indexing import embed as embed_module


class FakeEmbeddingsAPI:
    def create(self, model: str, input: list[str]) -> SimpleNamespace:
        return SimpleNamespace(
            data=[
                SimpleNamespace(embedding=[float(index)] * 1536)
                for index, _ in enumerate(input)
            ]
        )


class FakeOpenAIClient:
    def __init__(self, api_key: str) -> None:
        self.embeddings = FakeEmbeddingsAPI()


def test_embed_texts_uses_openai_client(monkeypatch) -> None:
    monkeypatch.setattr(embed_module, "OpenAI", FakeOpenAIClient)

    result = embed_module.embed_texts(["alpha", "beta"])

    assert len(result) == 2
    assert len(result[0]) == 1536

from app.core.config import settings
from app.engine.vector_store import get_collection, query_relevant_guidelines


class _FakeCollection:
    def __init__(self, documents: list[str]):
        self._documents = documents
        self.last_query: dict | None = None

    def count(self) -> int:
        return len(self._documents)

    def query(self, query_texts, n_results):
        self.last_query = {"query_texts": query_texts, "n_results": n_results}
        return {"documents": [self._documents[:n_results]]}


def test_query_relevant_guidelines_returns_empty_for_empty_collection():
    assert query_relevant_guidelines("cualquier hallazgo", collection=_FakeCollection([])) == []


def test_query_relevant_guidelines_caps_n_results_to_collection_size():
    fake = _FakeCollection(["directriz A", "directriz B"])

    result = query_relevant_guidelines("hallazgo", n_results=10, collection=fake)

    assert result == ["directriz A", "directriz B"]
    assert fake.last_query["n_results"] == 2


def test_query_relevant_guidelines_ranks_by_semantic_similarity(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "chromadb_path", str(tmp_path / "chroma"))
    get_collection.cache_clear()
    try:
        collection = get_collection()
        collection.upsert(
            ids=["ssh-guideline", "storage-guideline"],
            documents=[
                "Un puerto SSH o RDP abierto a 0.0.0.0/0 sin aislamiento de red es una "
                "exposición crítica salvo que exista un Bastion Host o VPN.",
                "Un Storage Account con acceso público restringido a una VNet privada "
                "reduce sustancialmente el riesgo de exfiltración de datos.",
            ],
            metadatas=[{"category": "network_exposure"}, {"category": "network_exposure"}],
        )

        results = query_relevant_guidelines(
            "NSG permite SSH desde Internet sin ningún Bastion Host", n_results=1
        )

        assert len(results) == 1
        assert "SSH" in results[0] or "RDP" in results[0]
    finally:
        get_collection.cache_clear()

"""Inicialización y acceso a la base de conocimientos vectorial en ChromaDB (HU-04)."""

from functools import lru_cache
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings


@lru_cache(maxsize=1)
def get_collection():
    """Cliente y colección de ChromaDB, cacheados: instanciar el modelo de
    embeddings en cada consulta sería prohibitivamente lento."""
    client = chromadb.PersistentClient(path=settings.chromadb_path)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.embeddings_model
    )
    return client.get_or_create_collection(
        name=settings.chromadb_collection,
        embedding_function=embedding_fn,
    )


def query_relevant_guidelines(
    query_text: str,
    n_results: int = settings.guideline_retrieval_count,
    collection: Any = None,
) -> list[str]:
    """Recupera, por similitud semántica, las directrices de seguridad más
    relevantes para `query_text` (típicamente la descripción de un hallazgo
    más su contexto de red).
    """
    collection = collection if collection is not None else get_collection()

    available = collection.count()
    if available == 0:
        return []

    result = collection.query(query_texts=[query_text], n_results=min(n_results, available))
    documents = result.get("documents") or [[]]
    return documents[0] if documents else []

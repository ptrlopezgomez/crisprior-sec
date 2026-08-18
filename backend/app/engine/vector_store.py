"""Inicialización y acceso a la base de conocimientos vectorial en ChromaDB (HU-04)."""

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings


def get_collection():
    client = chromadb.PersistentClient(path=settings.chromadb_path)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.embeddings_model
    )
    return client.get_or_create_collection(
        name=settings.chromadb_collection,
        embedding_function=embedding_fn,
    )

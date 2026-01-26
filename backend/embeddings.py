import os
from functools import lru_cache
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions


DEFAULT_COLLECTION_METADATA = {"hnsw:space": "cosine"}
DEFAULT_PERSIST_DIR = os.path.abspath(os.path.join("data", "chroma_db"))


@lru_cache(maxsize=1)
def get_embedding_function(model_name: str = "BAAI/bge-large-en-v1.5"):
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )


@lru_cache(maxsize=1)
def get_client(persist_dir: Optional[str] = None) -> chromadb.PersistentClient:
    persist_dir = persist_dir or DEFAULT_PERSIST_DIR
    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(
    collection_name: str,
    persist_dir: Optional[str] = None,
    model_name: str = "BAAI/bge-large-en-v1.5",
):
    client = get_client(persist_dir)
    embedding_fn = get_embedding_function(model_name)
    return client.get_or_create_collection(
        name=collection_name,
        metadata=DEFAULT_COLLECTION_METADATA,
        embedding_function=embedding_fn,
    )

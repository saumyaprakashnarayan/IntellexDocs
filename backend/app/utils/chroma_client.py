"""
app/utils/chroma_client.py
==========================
Wrapper around ChromaDB — the vector store that powers semantic search.

ChromaDB stores document chunk text alongside their float embedding vectors.
Given a query embedding, it finds the N stored vectors that are geometrically
closest, which corresponds to the N most semantically similar chunks.

This wrapper uses the PersistentClient API introduced in ChromaDB 0.4.
The old chromadb.Client(Settings(chroma_db_impl="duckdb+parquet")) API
was removed in that version and will raise an error if used.
"""

from pathlib import Path
from typing import Any

import chromadb

from app.core.config import settings


class ChromaClient:
    """
    Manages one ChromaDB PersistentClient instance shared across all requests.
    """

    def __init__(self) -> None:
        # The directory is created before ChromaDB is told about it because
        # ChromaDB raises if the path doesn't exist yet
        self.persist_directory: Path = settings.chroma_persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # PersistentClient writes every change to disk immediately after each mutation,
        # so no manual .persist() call is needed (that method was also removed in 0.4)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

    def get_collection(self, name: str) -> Any:
        """
        Returns an existing collection or creates a new one.
        get_or_create_collection is idempotent — calling it twice with the
        same name returns the same collection rather than raising an error.
        hnsw:space=cosine tells ChromaDB to measure distances using cosine
        similarity, which is the correct metric for normalised embedding vectors.
        """
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def delete_collection(self, name: str) -> None:
        """
        Removes the collection and all its stored vectors.
        The try/except silences the error when the collection doesn't exist,
        which is the expected state during the first run or after a reset.
        """
        try:
            self.client.delete_collection(name)
        except Exception:
            pass

    def search(
        self,
        collection_name: str,
        embeddings: list[float],
        n_results: int,
        filter: dict | None = None,
    ) -> dict:
        """
        Returns the N most similar chunks to the given query embedding.

        The where clause filters on metadata fields before computing similarity,
        so user_id filtering happens inside ChromaDB — not in Python — keeping
        one user's documents invisible to another user's queries.

        ChromaDB wraps results in an extra list because it supports batched
        queries. Since we always send one query at a time, we unwrap [0] to
        return flat lists that the pipeline can iterate directly.
        """
        collection = self.get_collection(collection_name)

        query_kwargs: dict[str, Any] = {
            "query_embeddings": [embeddings],
            "n_results": n_results,
            "include": ["metadatas", "documents", "distances", "ids"],
        }

        # An empty where dict causes a ChromaDB validation error, so it is
        # only attached when at least one filter criterion is present
        if filter:
            query_kwargs["where"] = filter

        raw = collection.query(**query_kwargs)

        # Unwrap the outer list produced by ChromaDB's batch-query interface
        return {
            "documents": raw["documents"][0] if raw.get("documents") else [],
            "metadatas": raw["metadatas"][0] if raw.get("metadatas") else [],
            "distances": raw["distances"][0] if raw.get("distances") else [],
            "ids":       raw["ids"][0]       if raw.get("ids")       else [],
        }

    def add(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        """
        Inserts chunks with their pre-computed embeddings into the collection.
        ChromaDB requires every item to have a unique string ID; we use
        "{document_id}_{page}_{chunk_index}" which is unique by construction
        and readable enough to trace back to the source during debugging.
        """
        collection = self.get_collection(collection_name)
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

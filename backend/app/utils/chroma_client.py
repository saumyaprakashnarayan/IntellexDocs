from pathlib import Path
from typing import Any, Iterable
import chromadb
from chromadb.config import Settings
from app.core.config import settings

class ChromaClient:
    def __init__(self) -> None:
        self.persist_directory: Path = settings.chroma_persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.persist_directory),
            )
        )

    def get_collection(self, name: str) -> Any:
        if name in [collection.name for collection in self.client.list_collections()]:
            return self.client.get_collection(name)
        return self.client.create_collection(name)

    def persist(self) -> None:
        self.client.persist()

    def delete_collection(self, name: str) -> None:
        if name in [collection.name for collection in self.client.list_collections()]:
            self.client.delete_collection(name)

    def search(self, collection_name: str, embeddings: list[float], n_results: int, filter: dict | None = None) -> dict:
        collection = self.get_collection(collection_name)
        return collection.query(
            query_embeddings=[embeddings],
            n_results=n_results,
            where=filter or {},
            include=['metadatas', 'documents', 'distances', 'ids'],
        )

    def add(self, collection_name: str, ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]]) -> None:
        collection = self.get_collection(collection_name)
        collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        self.persist()

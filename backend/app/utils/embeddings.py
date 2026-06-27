"""
app/utils/embeddings.py
=======================
Wraps the Google Generative AI embedding model behind a two-method interface.
Embedding models map text to dense float vectors; texts that mean similar
things end up geometrically close in that vector space, which is the
mathematical foundation that makes semantic search work.

Uses the google-genai SDK directly (not langchain_google_genai).
"""

from typing import Iterable

from google import genai

from app.core.config import settings


class EmbeddingService:
    """
    Holds a single initialised embedding client shared across all requests.
    The client is created on first use (lazy singleton in pipeline.py) so
    that a bad API key surfaces as a request-level error, not a startup crash.
    """

    def __init__(self) -> None:
        self.model_name = settings.gemini_embedding_model.removeprefix("models/")
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        """
        Vectorises a batch of document chunks in a single API call.
        Batching reduces the number of HTTP round-trips when ingesting a
        multi-page PDF — one call per chunk would be far too slow.
        """
        # The google.genai SDK embed_content treats a list of strings as multiple
        # parts of a single document (returning 1 embedding). To get one embedding
        # per chunk, we must call it individually.
        return [
            self.client.models.embed_content(
                model=self.model_name,
                contents=text,
            ).embeddings[0].values
            for text in texts
        ]

    def embed_query(self, query: str) -> list[float]:
        """
        Vectorises a single user question.
        Returns a flat list of floats that ChromaDB uses to rank chunks
        by cosine similarity against the query vector.
        """
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=[query],
        )
        return response.embeddings[0].values

"""
app/utils/embeddings.py
=======================
Wraps the Google Generative AI embedding model behind a two-method interface.
Embedding models map text to dense float vectors; texts that mean similar
things end up geometrically close in that vector space, which is the
mathematical foundation that makes semantic search work.
"""

from typing import Iterable

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings


class EmbeddingService:
    """
    Holds a single initialised embedding client that is shared across all
    requests. Constructing the client connects to the Gemini API and validates
    the API key, so doing it once at module import time surfaces auth errors early.
    """

    def __init__(self) -> None:
        self.model_name = settings.gemini_embedding_model
        # google_api_key is passed explicitly so the client does not fall back to
        # reading GOOGLE_API_KEY from the environment, which could silently use
        # the wrong key in a machine that has both variables set
        self.client = GoogleGenerativeAIEmbeddings(
            model=self.model_name,
            google_api_key=settings.gemini_api_key,
        )

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        """
        Vectorises a batch of document chunks in a single API call.
        Batching is important here because ingesting a 50-page PDF would
        otherwise make hundreds of individual HTTP requests to the Gemini API.
        """
        return self.client.embed_documents(list(texts))

    def embed_query(self, query: str) -> list[float]:
        """
        Vectorises a single user question.
        The Gemini embedding API uses a different internal prompt for query
        mode vs document mode, which improves retrieval accuracy — LangChain's
        embed_query() selects the correct mode automatically.
        """
        return self.client.embed_query(query)

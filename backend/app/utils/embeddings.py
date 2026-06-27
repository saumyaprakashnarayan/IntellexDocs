from typing import Iterable
<<<<<<< HEAD
from langchain.embeddings import GoogleGeminiEmbeddings
=======
from langchain_google_genai import GoogleGenerativeAIEmbeddings
>>>>>>> 33502da (chore)
from app.core.config import settings

class EmbeddingService:
    def __init__(self) -> None:
        self.model_name = settings.gemini_embedding_model
<<<<<<< HEAD
        self.client = GoogleGeminiEmbeddings(model=self.model_name, api_key=settings.gemini_api_key)
=======
        self.client = GoogleGenerativeAIEmbeddings(model=self.model_name, google_api_key=settings.gemini_api_key)
>>>>>>> 33502da (chore)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        return self.client.embed_documents(list(texts))

    def embed_query(self, query: str) -> list[float]:
        return self.client.embed_query(query)

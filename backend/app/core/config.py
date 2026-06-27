from pathlib import Path
from typing import List
<<<<<<< HEAD
from pydantic import BaseSettings, Field, AnyHttpUrl
=======
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings
>>>>>>> 33502da (chore)

class Settings(BaseSettings):
    environment: str = Field("development", env="ENVIRONMENT")
    postgres_dsn: str = Field("postgresql+asyncpg://postgres:postgres@postgres:5432/rag_db", env="DATABASE_URL")
    jwt_secret: str = Field("supersecretjwtkey", env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    uploads_dir: Path = Field(Path(__file__).resolve().parents[2] / "uploads")
    chroma_persist_directory: Path = Field(Path(__file__).resolve().parents[2] / "chroma_db")
    allowed_origins: List[AnyHttpUrl] = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.5-flash", env="GEMINI_MODEL")
    gemini_embedding_model: str = Field("embedding-001", env="GEMINI_EMBEDDING_MODEL")
    rag_chunk_size: int = Field(1000)
    rag_chunk_overlap: int = Field(200)
    semantic_search_k: int = Field(5)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

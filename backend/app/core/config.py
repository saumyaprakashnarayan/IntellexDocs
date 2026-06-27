"""
app/core/config.py
==================
Central settings object loaded once at startup and shared across the app.
Pydantic Settings reads values from environment variables first, then from
a .env file, then falls back to the defaults defined below.
"""

from pathlib import Path
from typing import List

from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Every configurable value in the application lives here.
    Importing `settings` from this module gives you a fully-resolved,
    type-validated configuration object — no raw os.getenv() calls elsewhere.
    """

    # Distinguishes local, staging and production behaviour in the codebase
    environment: str = Field("development", env="ENVIRONMENT")

    # asyncpg requires the postgresql+asyncpg:// scheme so SQLAlchemy uses
    # the async driver instead of the blocking psycopg2 one
    postgres_dsn: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db",
        env="DATABASE_URL",
    )

    # Signs every JWT token — a weak or leaked secret lets anyone forge tokens
    jwt_secret: str = Field("change-me-before-production", env="JWT_SECRET")

    # HS256 is symmetric HMAC-SHA256; the same secret both signs and verifies
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")

    # 24 hours gives users a full workday without re-logging in
    access_token_expire_minutes: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Resolved relative to the backend/ root so paths work regardless of
    # which directory the server is launched from
    uploads_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[2] / "uploads"
    )

    # ChromaDB writes its index files here; mounted as a Docker volume so
    # the vector database survives container rebuilds
    chroma_persist_directory: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[2] / "chroma_db"
    )

    # Browsers block cross-origin requests unless the server explicitly lists
    # the requesting origin here; wrong value causes silent fetch failures
    allowed_origins: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000"],
        env="ALLOWED_ORIGINS",
    )

    # Empty string makes every Gemini API call return 401 immediately
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")

    # Flash is faster and cheaper than Pro; swap for Pro on quality-sensitive tasks
    gemini_model: str = Field("gemini-2.5-flash", env="GEMINI_MODEL")

    # Must include the "models/" prefix that the Gemini embedding API requires
    gemini_embedding_model: str = Field(
        "models/embedding-001", env="GEMINI_EMBEDDING_MODEL"
    )

    # Larger chunks preserve more context per retrieval but cost more tokens
    rag_chunk_size: int = Field(1000)

    # Overlap prevents context from being silently cut at a chunk boundary
    rag_chunk_overlap: int = Field(200)

    # We fetch 2× this value from ChromaDB then filter, so the effective
    # top-K after ownership filtering is still this number
    semantic_search_k: int = Field(5)

    class Config:
        # .env is read only if the variable is not already in the environment;
        # real environment variables always take priority over the file
        env_file = ".env"
        env_file_encoding = "utf-8"


# Module-level singleton — instantiated once when Python imports this module,
# then shared everywhere via `from app.core.config import settings`
settings = Settings()

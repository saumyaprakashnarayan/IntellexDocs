"""
app/core/config.py
==================
Central settings object loaded once at startup and shared across the app.
Pydantic Settings reads values from environment variables first, then from
a .env file, then falls back to the defaults defined below.
"""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Every configurable value in the application lives here.
    Importing `settings` from this module gives you a fully-resolved,
    type-validated configuration object — no raw os.getenv() calls elsewhere.

    Field names map to environment variables by lowercasing the env var name:
      DATABASE_URL              → database_url
      JWT_SECRET                → jwt_secret
      ALLOWED_ORIGINS           → allowed_origins
      GEMINI_API_KEY            → gemini_api_key
    pydantic-settings 2.x performs this mapping automatically; explicit
    env= aliases are not needed and caused 'extra_forbidden' errors in v2.
    """

    # Distinguishes local, staging and production behaviour in the codebase
    environment: str = "development"

    # asyncpg requires the postgresql+asyncpg:// scheme so SQLAlchemy uses
    # the async driver instead of the blocking psycopg2 one.
    # Field name matches DATABASE_URL lowercased → database_url
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db"

    # Signs every JWT token — a weak or leaked secret lets anyone forge tokens
    jwt_secret: str = "change-me-before-production"

    # HS256 is symmetric HMAC-SHA256; the same secret both signs and verifies
    jwt_algorithm: str = "HS256"

    # 24 hours gives users a full workday without re-logging in
    access_token_expire_minutes: int = 60 * 24

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
    # the requesting origin here; wrong value causes silent fetch failures.
    # Plain str (not AnyHttpUrl) avoids pydantic adding a trailing slash that
    # breaks CORS: browser sends http://localhost:3000 but AnyHttpUrl stores
    # http://localhost:3000/ — they don't match and OPTIONS returns 400.
    # Must be JSON array in .env: ALLOWED_ORIGINS=["http://localhost:3000"]
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"],
    )

    # Empty string makes every Gemini API call return 401 immediately
    gemini_api_key: str = ""

    # Flash is faster and cheaper than Pro; swap for Pro on quality-sensitive tasks
    gemini_model: str = "gemini-2.5-flash"

    # Must include the "models/" prefix that the Gemini embedding API requires.
    # gemini-embedding-2 is the latest stable model available via this API key.
    gemini_embedding_model: str = "models/gemini-embedding-2"

    # Larger chunks preserve more context per retrieval but cost more tokens
    rag_chunk_size: int = 1000

    # Overlap prevents context from being silently cut at a chunk boundary
    rag_chunk_overlap: int = 200

    # We fetch 2× this value from ChromaDB then filter, so the effective
    # top-K after ownership filtering is still this number
    semantic_search_k: int = 5

    # pydantic-settings 2.x uses model_config instead of the deprecated inner
    # Config class. Real environment variables always take priority over .env.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # silently ignore any env vars not declared as fields
    )


# Module-level singleton — instantiated once when Python imports this module,
# then shared everywhere via `from app.core.config import settings`
settings = Settings()

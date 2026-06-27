"""
app/db/session.py
=================
Creates the async SQLAlchemy engine and session factory that every
database operation in this application runs through.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# A single engine is shared for the entire process lifetime.
# The engine owns a connection pool, so creating multiple engines
# would multiply the number of open connections to Postgres unnecessarily.
engine: AsyncEngine = create_async_engine(
    settings.postgres_dsn,
    future=True,       # enables the SQLAlchemy 2.0-style API throughout the codebase
    echo=False,        # set to True to print every SQL statement — useful when debugging queries
    pool_pre_ping=True, # issues a cheap SELECT before each query to discard stale connections
                        # that were silently closed by Postgres after a period of inactivity
)


# sessionmaker produces new AsyncSession objects on demand.
# expire_on_commit=False prevents SQLAlchemy from expiring ORM attributes
# immediately after a commit, which would trigger implicit lazy-loads and
# crash in an async context where IO can't happen outside an await
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Runs CREATE TABLE IF NOT EXISTS for every model that has been imported.
    Safe to call on an already-initialised database — it never drops tables.
    Called once from the application lifespan handler in main.py.
    """
    async with engine.begin() as conn:
        # The import here (not at module top) avoids a circular import:
        # models imports Base from db, and db.session is imported by models indirectly
        from app.db import models  # noqa: F401
        await conn.run_sync(models.Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    FastAPI dependency that opens an async DB session for exactly one request.
    The async context manager commits on clean exit and rolls back on exception,
    then returns the connection to the pool when the request is complete.
    """
    async with AsyncSessionLocal() as session:
        yield session

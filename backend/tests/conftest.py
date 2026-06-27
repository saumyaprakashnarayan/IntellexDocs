"""
tests/conftest.py
=================
Shared pytest fixtures for all backend tests.

asyncio_mode = "auto" is set in pytest.ini, so every async fixture and
test function is automatically run inside the event loop without needing
the @pytest.mark.asyncio decorator or a manual event_loop override.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.models import Base
from app.db.session import engine


@pytest.fixture(scope="session", autouse=True)
async def initialize_database():
    """
    Creates all tables before the test session and drops them afterwards.
    Using scope="session" means this runs once for the entire test suite,
    not once per test — faster and avoids recreating the schema repeatedly.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncClient:
    """
    Returns an HTTPX AsyncClient wired directly to the FastAPI app.
    ASGITransport connects the client to the app in-process without
    starting a real HTTP server, making tests fast and self-contained.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

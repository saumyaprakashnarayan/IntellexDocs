import asyncio
import pytest
from httpx import AsyncClient
from app.main import app
from app.db.models import Base
from app.db.session import engine

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

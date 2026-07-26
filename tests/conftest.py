import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

import app.database as db_module
from app.config import settings

# Reconfigure the engine to NullPool for tests only (see docstring above).
db_module.engine = create_async_engine(settings.database_url, echo=False, future=True, poolclass=NullPool)
db_module.AsyncSessionLocal = async_sessionmaker(
    bind=db_module.engine, class_=AsyncSession, expire_on_commit=False,
)

from app.database import Base, engine
from app.main import app





@pytest_asyncio.fixture(scope="function", autouse=True)
async def _fresh_schema():
    """Recreate all tables before each test so tests don't leak state into each other.

    Runs against the real Postgres instance configured in DATABASE_URL (see .env) —
    intentionally not SQLite, since the models use Postgres-specific UUID columns
    and we want tests to reflect the actual production database engine.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client):
    """Registers and logs in a user, returns (email, password, token_pair_json)."""
    email = "test_user@example.com"
    password = "correct-horse-battery-staple"
    await client.post("/auth/register", json={
        "email": email, "password": password, "full_name": "Test User"
    })
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return email, password, resp.json()

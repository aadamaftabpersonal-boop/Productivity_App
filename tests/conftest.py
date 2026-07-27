import os
os.environ["TESTING"] = "true"

import asyncio
import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import delete

import app.database as db_module
from app.config import settings

# Reconfigure engine with NullPool for test isolation
db_module.engine = create_async_engine(settings.database_url, echo=False, future=True, poolclass=NullPool)
db_module.AsyncSessionLocal = async_sessionmaker(
    bind=db_module.engine, class_=AsyncSession, expire_on_commit=False,
)

from app.database import Base, engine, AsyncSessionLocal
from app.models import User, CodeSubmission, ReviewResult, WeaknessRecord
from app.main import app

app.state.limiter.enabled = False


@pytest_asyncio.fixture(scope="function", autouse=True)
async def _fresh_schema():
    """Ensure database tables exist and clean up test rows without dropping production tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Teardown: clean up test user rows so dev data is preserved
    async with AsyncSessionLocal() as session:
        await session.execute(delete(User).where(User.email.like("%@%")))
        await session.commit()



@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client):
    """Registers and logs in a test user, returns (email, password, token_pair_json)."""
    email = "test_user@example.com"
    password = "correct-horse-battery-staple"
    await client.post("/auth/register", json={
        "email": email, "password": password, "full_name": "Test User"
    })
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return email, password, resp.json()

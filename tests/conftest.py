import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text as sa_text
from sqlalchemy.schema import DefaultClause
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.cache import cache
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


# Replace PostgreSQL now() with SQLite CURRENT_TIMESTAMP (once at import time)
for table in Base.metadata.tables.values():
    for column in table.columns:
        if column.server_default is not None:
            try:
                default_text = column.server_default.arg.text
            except AttributeError:
                continue
            if "now()" in default_text:
                column.server_default = DefaultClause(sa_text("CURRENT_TIMESTAMP"))


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    cache._store.clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def auth_headers():
    """Returns auth headers with a valid JWT for user id=1."""
    token = create_access_token(data={"sub": "1", "username": "testuser"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def registered_user(client: AsyncClient):
    """Register a test user and return the response data."""
    payload = {
        "full_name": "Test User",
        "username": "testuser",
        "phone_number": "08123456789",
        "email": "test@example.com",
        "password": "securepassword123",
    }
    response = await client.post("/auth/register", json=payload)
    return response.json()


@pytest.fixture
async def auth_token(client: AsyncClient, registered_user):
    """Login and return a valid token + headers."""
    response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "securepassword123",
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

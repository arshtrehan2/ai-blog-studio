import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.database import Base, get_db
from app.modules.auth.service import create_access_token
from app.modules.auth.models import User
from app.modules.auth.schemas import SignupRequest
from app.modules.ai.rate_limiter import get_rate_limiter, RateLimiter

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


def _make_session_factory(engine):
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def _make_db_override(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    return override_get_db


def _make_permissive_rate_limiter():
    mock_limiter = AsyncMock(spec=RateLimiter)
    mock_limiter.check = AsyncMock(return_value=(True, 0))

    async def _allow():
        return mock_limiter

    return _allow


@pytest_asyncio.fixture(scope="function")
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = _make_session_factory(test_engine)
    app = create_app()
    app.dependency_overrides[get_db] = _make_db_override(session_factory)
    app.dependency_overrides[get_rate_limiter] = _make_permissive_rate_limiter()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def rate_limited_client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = _make_session_factory(test_engine)
    app = create_app()
    app.dependency_overrides[get_db] = _make_db_override(session_factory)

    mock_limiter = AsyncMock(spec=RateLimiter)
    mock_limiter.check = AsyncMock(return_value=(False, 3600))

    async def _block():
        return mock_limiter

    app.dependency_overrides[get_rate_limiter] = _block

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    from app.modules.auth.service import create_user
    data = SignupRequest(
        email="test@example.com",
        password="testpassword123",
        display_name="Test User",
    )
    user = await create_user(db_session, data)
    await db_session.commit()
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    return create_access_token(str(test_user.id))


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    return {"Authorization": f"Bearer {user_token}"}

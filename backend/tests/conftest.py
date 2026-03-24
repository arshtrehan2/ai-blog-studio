"""
pytest configuration and shared fixtures for AI Blog Studio backend tests.

Uses SQLite in-memory database to avoid needing a live PostgreSQL instance.
Redis calls are mocked via unittest.mock.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Use SQLite for tests (no PostgreSQL needed)
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create a single SQLite engine for the entire test session."""
    from app.database import Base
    # Import all models so tables are created
    from app.modules.auth.models import User  # noqa
    from app.modules.posts.models import Post, Tag, PostTag, AIUsageLog  # noqa

    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key support in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(engine) -> Session:
    """Provide a transactional test database session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    TestSessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = TestSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with DB and Redis mocked."""
    from app.main import app
    from app.database import get_db

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Mock Redis so tests don't need a live Redis instance
    with patch("app.modules.ai.rate_limiter._get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        # Simulate pipeline that returns [0, 0, ...] (no rate-limit breach)
        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = [0, 0, 0, 0]
        mock_redis.pipeline.return_value = mock_pipeline
        mock_redis.zrange.return_value = []
        mock_redis_factory.return_value = mock_redis

        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()


# ── Auth helpers ───────────────────────────────────────────────────────────

@pytest.fixture()
def registered_user(client):
    """Register a user and return (user_data, token)."""
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "display_name": "Test User",
    }
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["user"], data["access_token"]


@pytest.fixture()
def auth_headers(registered_user):
    """Return Authorization headers for the registered user."""
    _, token = registered_user
    return {"Authorization": f"Bearer {token}"}

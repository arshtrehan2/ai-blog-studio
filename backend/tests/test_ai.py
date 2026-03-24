"""Tests for the AI module — TDD first (mocked Claude API)."""
import uuid
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient

from app.modules.auth.models import User
from app.modules.ai.prompts import (
    IMPROVE_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT, TAGS_SYSTEM_PROMPT,
    SEO_TITLE_SYSTEM_PROMPT, TLDR_SYSTEM_PROMPT,
)


# ──────────────────────────────────────────────
# Prompt constant tests
# ──────────────────────────────────────────────

def test_improve_prompt_contains_key_instructions():
    assert "editor" in IMPROVE_SYSTEM_PROMPT.lower()
    assert "return only" in IMPROVE_SYSTEM_PROMPT.lower()


def test_summary_prompt_has_placeholder():
    assert "{max_sentences}" in SUMMARY_SYSTEM_PROMPT
    formatted = SUMMARY_SYSTEM_PROMPT.format(max_sentences=3)
    assert "3-sentence" in formatted or "3" in formatted


def test_tags_prompt_has_placeholder():
    assert "{max_tags}" in TAGS_SYSTEM_PROMPT
    formatted = TAGS_SYSTEM_PROMPT.format(max_tags=5)
    assert "5" in formatted


def test_seo_title_prompt_mentions_json():
    assert "json" in SEO_TITLE_SYSTEM_PROMPT.lower()
    assert "seo_title" in SEO_TITLE_SYSTEM_PROMPT


def test_tldr_prompt_mentions_sentence():
    assert "sentence" in TLDR_SYSTEM_PROMPT.lower()


# ──────────────────────────────────────────────
# Schema validation tests
# ──────────────────────────────────────────────

def test_improve_request_validates_content():
    from app.modules.ai.schemas import ImproveRequest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ImproveRequest(content="")


def test_improve_request_validates_max_length():
    from app.modules.ai.schemas import ImproveRequest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ImproveRequest(content="x" * 10001)


def test_summary_request_defaults():
    from app.modules.ai.schemas import SummaryRequest
    req = SummaryRequest(content="Some content")
    assert req.max_sentences == 3


def test_tags_request_defaults():
    from app.modules.ai.schemas import TagsRequest
    req = TagsRequest(content="Some content")
    assert req.max_tags == 5


# ──────────────────────────────────────────────
# Rate limiter tests (mocked Redis)
# ──────────────────────────────────────────────

async def test_rate_limit_allows_first_request():
    from app.modules.ai.rate_limiter import check_rate_limit

    mock_redis = AsyncMock()
    mock_redis.pipeline.return_value.__aenter__ = AsyncMock(return_value=mock_redis)
    mock_redis.pipeline.return_value.__aexit__ = AsyncMock(return_value=None)

    # Build a proper pipeline mock
    pipeline_mock = MagicMock()
    pipeline_mock.zremrangebyscore = MagicMock()
    pipeline_mock.zcard = MagicMock()
    pipeline_mock.zadd = MagicMock()
    pipeline_mock.expire = MagicMock()
    pipeline_mock.execute = AsyncMock(return_value=[0, 0, 1, True])  # count=0 before adding

    mock_redis.pipeline = MagicMock(return_value=pipeline_mock)

    user_id = uuid.uuid4()
    allowed, retry_after = await check_rate_limit(user_id, mock_redis)
    assert allowed is True
    assert retry_after == 0


async def test_rate_limit_blocks_when_exceeded():
    from app.modules.ai.rate_limiter import check_rate_limit
    import time

    mock_redis = AsyncMock()
    pipeline_mock = MagicMock()
    pipeline_mock.zremrangebyscore = MagicMock()
    pipeline_mock.zcard = MagicMock()
    pipeline_mock.zadd = MagicMock()
    pipeline_mock.expire = MagicMock()
    # count=20 means we've hit the limit
    pipeline_mock.execute = AsyncMock(return_value=[0, 20, 1, True])

    mock_redis.pipeline = MagicMock(return_value=pipeline_mock)

    now = time.time()
    oldest_time = now - 3500  # 3500 seconds ago in the window
    mock_redis.zrange = AsyncMock(return_value=[(str(oldest_time), oldest_time)])
    mock_redis.zrem = AsyncMock(return_value=1)

    user_id = uuid.uuid4()
    allowed, retry_after = await check_rate_limit(user_id, mock_redis)
    assert allowed is False
    assert retry_after > 0


# ──────────────────────────────────────────────
# HTTP endpoint tests (mocked Claude + Redis)
# ──────────────────────────────────────────────

def make_claude_response(text: str):
    """Build a mock Anthropic message response."""
    mock_content = MagicMock()
    mock_content.text = text
    mock_usage = MagicMock()
    mock_usage.input_tokens = 100
    mock_usage.output_tokens = 50
    mock_msg = MagicMock()
    mock_msg.content = [mock_content]
    mock_msg.usage = mock_usage
    return mock_msg


def make_allowed_redis():
    """Build a mock Redis that always allows requests."""
    pipeline_mock = MagicMock()
    pipeline_mock.zremrangebyscore = MagicMock()
    pipeline_mock.zcard = MagicMock()
    pipeline_mock.zadd = MagicMock()
    pipeline_mock.expire = MagicMock()
    pipeline_mock.execute = AsyncMock(return_value=[0, 0, 1, True])

    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=pipeline_mock)
    return mock_redis


def make_blocked_redis():
    """Build a mock Redis that blocks requests (rate limit exceeded)."""
    import time
    pipeline_mock = MagicMock()
    pipeline_mock.execute = AsyncMock(return_value=[0, 20, 1, True])
    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=pipeline_mock)
    now = time.time()
    oldest = now - 3500
    mock_redis.zrange = AsyncMock(return_value=[(str(oldest), oldest)])
    mock_redis.zrem = AsyncMock(return_value=1)
    return mock_redis


@pytest.fixture
def mock_redis_allowed():
    return make_allowed_redis()


@pytest.fixture
def mock_redis_blocked():
    return make_blocked_redis()


async def test_improve_endpoint_success(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app

    mock_response = make_claude_response("Improved content here.")

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/improve", json={"content": "Some blog content to improve."}, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    data = resp.json()
    assert "improved_content" in data
    assert data["improved_content"] == "Improved content here."
    assert "model" in data
    assert "usage" in data
    assert data["usage"]["input_tokens"] == 100
    assert data["usage"]["output_tokens"] == 50


async def test_improve_endpoint_unauthenticated(client: AsyncClient):
    resp = await client.post("/ai/improve", json={"content": "Some content"})
    assert resp.status_code == 401


async def test_improve_endpoint_empty_content(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app
    app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
    resp = await client.post("/ai/improve", json={"content": ""}, headers=auth_headers)
    app.dependency_overrides.pop(get_redis, None)
    assert resp.status_code == 422


async def test_improve_endpoint_content_too_long(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app
    app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
    resp = await client.post("/ai/improve", json={"content": "x" * 10001}, headers=auth_headers)
    app.dependency_overrides.pop(get_redis, None)
    assert resp.status_code == 422


async def test_improve_endpoint_rate_limited(client: AsyncClient, auth_headers: dict, mock_redis_blocked):
    from app.modules.ai.router import get_redis
    from app.main import app

    app.dependency_overrides[get_redis] = lambda: mock_redis_blocked
    resp = await client.post("/ai/improve", json={"content": "Some content"}, headers=auth_headers)
    app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 429
    assert "Rate limit" in resp.json()["detail"]
    assert "Retry-After" in resp.headers


async def test_summary_endpoint_success(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app

    mock_response = make_claude_response("This is a short summary.")

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/summary", json={"content": "Long article content here.", "max_sentences": 2}, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "This is a short summary."
    assert "model" in data


async def test_tags_endpoint_success(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app

    mock_response = make_claude_response('["python", "fastapi", "web-development"]')

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/tags", json={"content": "Article about Python and FastAPI.", "max_tags": 3}, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["tags"], list)
    assert "python" in data["tags"]


async def test_tags_endpoint_handles_invalid_json(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    """Tags endpoint should handle non-JSON Claude response gracefully."""
    from app.modules.ai.router import get_redis
    from app.main import app

    mock_response = make_claude_response("python, fastapi, web")  # Not JSON

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/tags", json={"content": "Some content"}, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["tags"], list)  # Returns empty list on parse failure


async def test_seo_title_endpoint_success(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app

    seo_data = {"seo_title": "Best Python Guide 2024", "seo_description": "Learn Python with FastAPI in this comprehensive guide."}
    mock_response = make_claude_response(json.dumps(seo_data))

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/seo-title", json={
            "content": "Guide about Python and FastAPI",
            "title": "Python Guide",
            "target_keyword": "Python FastAPI",
        }, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["seo_title"] == "Best Python Guide 2024"
    assert "seo_description" in data


async def test_tldr_endpoint_success(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app

    mock_response = make_claude_response("A quick TLDR in one sentence.")

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/tldr", json={"content": "Long article content here."}, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["tldr"] == "A quick TLDR in one sentence."
    assert "model" in data
    assert "usage" in data


async def test_ai_logs_usage_to_db(client: AsyncClient, auth_headers: dict, mock_redis_allowed, db_session):
    """Verify AI calls log usage to the ai_usage_log table."""
    from app.modules.ai.router import get_redis
    from app.main import app
    from app.modules.posts.models import AIUsageLog
    from sqlalchemy import select

    mock_response = make_claude_response("Improved content.")

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/improve", json={"content": "Content to improve."}, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200

    result = await db_session.execute(select(AIUsageLog).where(AIUsageLog.tool == "improve"))
    logs = result.scalars().all()
    assert len(logs) >= 1
    log = logs[-1]
    assert log.input_tokens == 100
    assert log.output_tokens == 50


async def test_improve_with_context(client: AsyncClient, auth_headers: dict, mock_redis_allowed):
    from app.modules.ai.router import get_redis
    from app.main import app

    mock_response = make_claude_response("Improved with context.")

    with patch("app.modules.ai.service.get_anthropic_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.messages.create = MagicMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        app.dependency_overrides[get_redis] = lambda: mock_redis_allowed
        resp = await client.post("/ai/improve", json={
            "content": "Blog content here.",
            "context": "technical blog post about Python"
        }, headers=auth_headers)
        app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    assert resp.json()["improved_content"] == "Improved with context."

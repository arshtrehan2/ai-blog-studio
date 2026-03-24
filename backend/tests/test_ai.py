import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient

from app.modules.ai.prompts import (
    IMPROVE_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT,
    TAGS_SYSTEM_PROMPT, SEO_TITLE_SYSTEM_PROMPT, TLDR_SYSTEM_PROMPT,
)


class TestPrompts:
    def test_improve_prompt_exists(self):
        assert "rewrite" in IMPROVE_SYSTEM_PROMPT.lower() or "editor" in IMPROVE_SYSTEM_PROMPT.lower()

    def test_summary_prompt_has_placeholder(self):
        assert "{max_sentences}" in SUMMARY_SYSTEM_PROMPT
        assert "3" in SUMMARY_SYSTEM_PROMPT.format(max_sentences=3)

    def test_tags_prompt_has_placeholder(self):
        assert "{max_tags}" in TAGS_SYSTEM_PROMPT

    def test_seo_title_prompt_mentions_json(self):
        assert "JSON" in SEO_TITLE_SYSTEM_PROMPT

    def test_tldr_prompt_exists(self):
        assert len(TLDR_SYSTEM_PROMPT) > 0


class TestAISchemas:
    def test_improve_request_validates_max_length(self):
        from app.modules.ai.schemas import ImproveRequest
        with pytest.raises(Exception):
            ImproveRequest(content="x" * 10001)

    def test_improve_request_validates_empty(self):
        from app.modules.ai.schemas import ImproveRequest
        with pytest.raises(Exception):
            ImproveRequest(content="   ")

    def test_summary_default_max_sentences(self):
        from app.modules.ai.schemas import SummaryRequest
        assert SummaryRequest(content="Some content.").max_sentences == 3

    def test_tags_default_max_tags(self):
        from app.modules.ai.schemas import TagsRequest
        assert TagsRequest(content="Some content.").max_tags == 5


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests():
    from app.modules.ai.rate_limiter import RateLimiter
    mock_redis = MagicMock()
    mock_pipe = AsyncMock()
    mock_redis.pipeline.return_value = mock_pipe
    mock_pipe.zremrangebyscore = AsyncMock(return_value=None)
    mock_pipe.zcard = AsyncMock(return_value=None)
    mock_pipe.zadd = AsyncMock(return_value=None)
    mock_pipe.expire = AsyncMock(return_value=None)
    mock_pipe.execute = AsyncMock(return_value=[None, 5, None, None])
    limiter = RateLimiter(mock_redis)
    allowed, retry_after = await limiter.check("user-123")
    assert allowed is True and retry_after == 0


@pytest.mark.asyncio
async def test_rate_limiter_blocks_when_exceeded():
    from app.modules.ai.rate_limiter import RateLimiter
    import time
    mock_redis = MagicMock()
    mock_pipe = AsyncMock()
    mock_redis.pipeline.return_value = mock_pipe
    mock_pipe.zremrangebyscore = AsyncMock(return_value=None)
    mock_pipe.zcard = AsyncMock(return_value=None)
    mock_pipe.zadd = AsyncMock(return_value=None)
    mock_pipe.expire = AsyncMock(return_value=None)
    mock_pipe.execute = AsyncMock(return_value=[None, 20, None, None])
    mock_redis.zrem = AsyncMock(return_value=1)
    mock_redis.zrange = AsyncMock(return_value=[("ts", time.time() - 100)])
    limiter = RateLimiter(mock_redis)
    allowed, retry_after = await limiter.check("user-123")
    assert allowed is False and retry_after > 0


def _mock_claude(text, input_tokens=100, output_tokens=50):
    m = MagicMock()
    m.content = [MagicMock(text=text)]
    m.usage.input_tokens = input_tokens
    m.usage.output_tokens = output_tokens
    return m


@pytest.mark.asyncio
async def test_ai_improve_success(client: AsyncClient, auth_headers: dict):
    with patch("app.modules.ai.service._get_client") as mock_c:
        mock_c.return_value.messages.create.return_value = _mock_claude("Improved content.")
        response = await client.post("/ai/improve", json={"content": "Original content."}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["improved_content"] == "Improved content."
    assert response.json()["usage"]["input_tokens"] == 100


@pytest.mark.asyncio
async def test_ai_improve_requires_auth(client: AsyncClient):
    response = await client.post("/ai/improve", json={"content": "Some content."})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_ai_improve_rate_limited(rate_limited_client: AsyncClient):
    signup = await rate_limited_client.post("/auth/signup", json={
        "email": "rl@example.com", "password": "password123", "display_name": "RL"})
    headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}
    response = await rate_limited_client.post("/ai/improve", json={"content": "Content."}, headers=headers)
    assert response.status_code == 429
    assert "Retry-After" in response.headers


@pytest.mark.asyncio
async def test_ai_summary_success(client: AsyncClient, auth_headers: dict):
    with patch("app.modules.ai.service._get_client") as mock_c:
        mock_c.return_value.messages.create.return_value = _mock_claude("A 3-sentence summary.")
        response = await client.post("/ai/summary", json={"content": "Long article.", "max_sentences": 3}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["summary"] == "A 3-sentence summary."


@pytest.mark.asyncio
async def test_ai_tags_success(client: AsyncClient, auth_headers: dict):
    with patch("app.modules.ai.service._get_client") as mock_c:
        mock_c.return_value.messages.create.return_value = _mock_claude(json.dumps(["python", "fastapi"]))
        response = await client.post("/ai/tags", json={"content": "Article about Python."}, headers=auth_headers)
    assert response.status_code == 200
    assert "python" in response.json()["tags"]


@pytest.mark.asyncio
async def test_ai_seo_title_success(client: AsyncClient, auth_headers: dict):
    seo_data = json.dumps({"seo_title": "Build REST APIs", "seo_description": "A guide to REST APIs."})
    with patch("app.modules.ai.service._get_client") as mock_c:
        mock_c.return_value.messages.create.return_value = _mock_claude(seo_data)
        response = await client.post("/ai/seo-title", json={"content": "Article."}, headers=auth_headers)
    assert response.status_code == 200
    assert "seo_title" in response.json()
    assert len(response.json()["seo_title"]) <= 60


@pytest.mark.asyncio
async def test_ai_tldr_success(client: AsyncClient, auth_headers: dict):
    with patch("app.modules.ai.service._get_client") as mock_c:
        mock_c.return_value.messages.create.return_value = _mock_claude("FastAPI is awesome.")
        response = await client.post("/ai/tldr", json={"content": "A long article."}, headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["tldr"]) > 0


@pytest.mark.asyncio
async def test_ai_improve_content_too_long(client: AsyncClient, auth_headers: dict):
    response = await client.post("/ai/improve", json={"content": "x" * 10001}, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_tldr_content_too_long(client: AsyncClient, auth_headers: dict):
    response = await client.post("/ai/tldr", json={"content": "x" * 10001}, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_usage_logged_after_improve(client: AsyncClient, auth_headers: dict):
    with patch("app.modules.ai.service._get_client") as mock_c:
        mock_c.return_value.messages.create.return_value = _mock_claude("Improved.", input_tokens=200, output_tokens=100)
        response = await client.post("/ai/improve", json={"content": "Original."}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["usage"]["input_tokens"] == 200

import pytest
from unittest.mock import MagicMock, patch


def _make_claude_response(text: str):
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    response.model = "claude-3-5-sonnet-20241022"
    response.usage.input_tokens = 100
    response.usage.output_tokens = 50
    return response


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Patch the redis client in rate_limiter to avoid real Redis calls."""
    mock = MagicMock()
    pipe = MagicMock()
    # zremrangebyscore=None, zcard=0, zadd=None, expire=None
    pipe.execute.return_value = [None, 0, None, None]
    mock.pipeline.return_value = pipe
    mock.zrange.return_value = []

    import app.modules.ai.rate_limiter as rl
    monkeypatch.setattr(rl, "_redis_client", mock)
    return mock


def test_improve_content(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            "This is improved content."
        )
        response = client.post(
            "/ai/improve",
            json={"content": "Some text to improve."},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert "improved_content" in data
    assert data["improved_content"] == "This is improved content."
    assert "model" in data
    assert "usage" in data
    assert data["usage"]["input_tokens"] == 100
    assert data["usage"]["output_tokens"] == 50


def test_improve_with_context(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            "Improved with context."
        )
        response = client.post(
            "/ai/improve",
            json={"content": "Some text.", "context": "technical blog post"},
            headers=auth_headers,
        )
    assert response.status_code == 200


def test_generate_summary(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            "A concise summary."
        )
        response = client.post(
            "/ai/summary",
            json={"content": "Long article content.", "max_sentences": 2},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"] == "A concise summary."


def test_generate_tags(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            '["python", "fastapi", "backend"]'
        )
        response = client.post(
            "/ai/tags",
            json={"content": "Article about Python FastAPI.", "max_tags": 3},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)
    assert "python" in data["tags"]


def test_generate_tags_with_title(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            '["go", "performance"]'
        )
        response = client.post(
            "/ai/tags",
            json={"content": "Article body.", "title": "Go Performance", "max_tags": 2},
            headers=auth_headers,
        )
    assert response.status_code == 200


def test_generate_seo_title(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            '{"seo_title": "Best Python Guide 2024", "seo_description": "Learn Python fast."}'
        )
        response = client.post(
            "/ai/seo-title",
            json={"content": "Article about Python."},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["seo_title"] == "Best Python Guide 2024"
    assert data["seo_description"] == "Learn Python fast."


def test_generate_tldr(client, auth_headers):
    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response(
            "TLDR: This is a great article about AI blogging."
        )
        response = client.post(
            "/ai/tldr",
            json={"content": "Long article content here."},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert "tldr" in data
    assert "model" in data


def test_ai_requires_authentication(client):
    response = client.post("/ai/improve", json={"content": "test"})
    assert response.status_code == 403


def test_rate_limit_exceeded(client, auth_headers, monkeypatch):
    import app.modules.ai.rate_limiter as rl

    mock = MagicMock()
    pipe = MagicMock()
    # Return count = 20 => at limit
    pipe.execute.return_value = [None, 20, None, None]
    mock.pipeline.return_value = pipe
    mock.zrange.return_value = [("1700000000.0", 1700000000.0)]
    monkeypatch.setattr(rl, "_redis_client", mock)

    with patch("app.modules.ai.service.get_anthropic_client"):
        response = client.post(
            "/ai/improve",
            json={"content": "test"},
            headers=auth_headers,
        )
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]


def test_ai_usage_logged(client, auth_headers, db):
    """Verify that AI usage is recorded in the database."""
    from app.modules.ai.models import AIUsageLog

    with patch("app.modules.ai.service.get_anthropic_client") as mock_ac:
        mock_ac.return_value.messages.create.return_value = _make_claude_response("Done.")
        client.post(
            "/ai/improve",
            json={"content": "Test content."},
            headers=auth_headers,
        )
    logs = db.query(AIUsageLog).all()
    assert len(logs) == 1
    assert logs[0].tool == "improve"
    assert logs[0].input_tokens == 100
    assert logs[0].output_tokens == 50

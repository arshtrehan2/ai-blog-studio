"""
TDD tests for the AI module.

Covers:
- POST /ai/improve    (200, 401, 422, 429)
- POST /ai/summary    (200, 401)
- POST /ai/tags       (200, 401)
- POST /ai/seo-title  (200, 401)
- POST /ai/tldr       (200, 401)
- Rate limiting       (429)
"""
import json
from unittest.mock import MagicMock, patch
import pytest


# ── Claude mock helpers ──────────────────────────────────────────────────────

def _make_claude_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    msg.usage.input_tokens = 100
    msg.usage.output_tokens = 50
    return msg


# ── Improve ─────────────────────────────────────────────────────────────────

def test_improve_success(client, auth_headers):
    improved = "This is an improved version of the text."
    with patch("app.modules.ai.service._get_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(improved)
        mock_factory.return_value = mock_client

        resp = client.post(
            "/ai/improve",
            json={"content": "This is some text."},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["improved_content"] == improved
    assert "model" in data
    assert data["usage"]["input_tokens"] == 100
    assert data["usage"]["output_tokens"] == 50


def test_improve_unauthenticated(client):
    resp = client.post("/ai/improve", json={"content": "Some content."})
    assert resp.status_code == 401


def test_improve_empty_content(client, auth_headers):
    resp = client.post("/ai/improve", json={"content": "   "}, headers=auth_headers)
    assert resp.status_code == 422


def test_improve_content_too_long(client, auth_headers):
    resp = client.post(
        "/ai/improve",
        json={"content": "x" * 10_001},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── Summary ─────────────────────────────────────────────────────────────────

def test_summary_success(client, auth_headers):
    summary_text = "This is a 3-sentence summary."
    with patch("app.modules.ai.service._get_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(summary_text)
        mock_factory.return_value = mock_client

        resp = client.post(
            "/ai/summary",
            json={"content": "A very long article about Python.", "max_sentences": 3},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json()["summary"] == summary_text


def test_summary_unauthenticated(client):
    resp = client.post("/ai/summary", json={"content": "Some content."})
    assert resp.status_code == 401


# ── Tags ────────────────────────────────────────────────────────────────────

def test_tags_success(client, auth_headers):
    tag_list = ["python", "fastapi", "backend", "api", "web"]
    with patch("app.modules.ai.service._get_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(json.dumps(tag_list))
        mock_factory.return_value = mock_client

        resp = client.post(
            "/ai/tags",
            json={"content": "Article about FastAPI.", "max_tags": 5},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json()["tags"] == tag_list


def test_tags_unauthenticated(client):
    resp = client.post("/ai/tags", json={"content": "Some content."})
    assert resp.status_code == 401


# ── SEO Title ───────────────────────────────────────────────────────────────

def test_seo_title_success(client, auth_headers):
    seo_payload = {"seo_title": "Best FastAPI Guide", "seo_description": "Learn FastAPI fast."}
    with patch("app.modules.ai.service._get_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(json.dumps(seo_payload))
        mock_factory.return_value = mock_client

        resp = client.post(
            "/ai/seo-title",
            json={"content": "A guide to FastAPI."},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["seo_title"] == seo_payload["seo_title"]
    assert data["seo_description"] == seo_payload["seo_description"]


def test_seo_title_unauthenticated(client):
    resp = client.post("/ai/seo-title", json={"content": "Some content."})
    assert resp.status_code == 401


# ── TLDR ────────────────────────────────────────────────────────────────────

def test_tldr_success(client, auth_headers):
    tldr_text = "FastAPI is fast and easy."
    with patch("app.modules.ai.service._get_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_claude_response(tldr_text)
        mock_factory.return_value = mock_client

        resp = client.post(
            "/ai/tldr",
            json={"content": "A guide to FastAPI."},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json()["tldr"] == tldr_text


def test_tldr_unauthenticated(client):
    resp = client.post("/ai/tldr", json={"content": "Some content."})
    assert resp.status_code == 401


# ── Rate limiting ─────────────────────────────────────────────────────────────

def test_rate_limit_exceeded(client, auth_headers):
    """
    When the Redis sliding window returns count >= limit, the endpoint returns 429.
    """
    with patch("app.modules.ai.rate_limiter._get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        mock_pipeline = MagicMock()
        # Simulate 20 existing requests (at limit)
        mock_pipeline.execute.return_value = [0, 20, 0, 0]
        mock_redis.pipeline.return_value = mock_pipeline
        mock_redis.zrange.return_value = [("1700000000", 1700000000.0)]
        mock_redis_factory.return_value = mock_redis

        resp = client.post(
            "/ai/improve",
            json={"content": "Some text."},
            headers=auth_headers,
        )
    assert resp.status_code == 429
    assert "rate limit" in resp.json()["detail"].lower()

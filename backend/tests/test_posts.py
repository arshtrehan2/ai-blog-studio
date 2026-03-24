"""
TDD tests for the Posts module.

Covers:
- POST   /posts              (201, 401, 422)
- GET    /posts              (200 with pagination / tag filter)
- GET    /posts/{id}         (200, 403 for drafts, 404)
- PUT    /posts/{id}         (200, 403, 404)
- DELETE /posts/{id}         (204, 403, 404)
- PATCH  /posts/{id}/publish (200, 400, 403)
"""
import pytest


# ── Helpers ────────────────────────────────────────────────────────────────

def _create_post(client, auth_headers, **overrides):
    payload = {
        "title": "My First Post",
        "content": "Hello world!",
        "tags": ["python", "fastapi"],
        "status": "draft",
        **overrides,
    }
    return client.post("/posts", json=payload, headers=auth_headers)


def _second_user(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "second@example.com", "password": "password123", "display_name": "Second"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Create ─────────────────────────────────────────────────────────────────

def test_create_post_success(client, auth_headers):
    resp = _create_post(client, auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My First Post"
    assert data["status"] == "draft"
    assert "python" in data["tags"]
    assert "fastapi" in data["tags"]
    assert "slug" in data
    assert data["slug"]  # non-empty


def test_create_post_unauthenticated(client):
    resp = client.post(
        "/posts",
        json={"title": "Test", "content": "body"},
    )
    assert resp.status_code == 401


def test_create_post_missing_title(client, auth_headers):
    resp = client.post("/posts", json={"content": "body"}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_post_published_sets_published_at(client, auth_headers):
    resp = _create_post(client, auth_headers, status="published")
    assert resp.status_code == 201
    assert resp.json()["status"] == "published"
    assert resp.json()["published_at"] is not None


# ── List ───────────────────────────────────────────────────────────────────

def test_list_posts_empty(client):
    resp = client.get("/posts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_posts_returns_only_published(client, auth_headers):
    _create_post(client, auth_headers, status="draft")  # should NOT appear
    _create_post(client, auth_headers, title="Pub Post", status="published")  # should appear
    resp = client.get("/posts")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Pub Post"


def test_list_posts_tag_filter(client, auth_headers):
    _create_post(client, auth_headers, title="Tagged", status="published", tags=["python"])
    _create_post(client, auth_headers, title="No Match", status="published", tags=["golang"])
    resp = client.get("/posts?tag=python")
    assert resp.status_code == 200
    items = resp.json()["items"]
    titles = [i["title"] for i in items]
    assert "Tagged" in titles
    assert "No Match" not in titles


def test_list_posts_pagination(client, auth_headers):
    for i in range(5):
        _create_post(client, auth_headers, title=f"Post {i}", status="published")
    resp = client.get("/posts?page=1&page_size=3")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 5
    assert data["total_pages"] == 2


# ── Get single ──────────────────────────────────────────────────────────────

def test_get_published_post_no_auth(client, auth_headers):
    resp = _create_post(client, auth_headers, status="published")
    post_id = resp.json()["id"]
    r = client.get(f"/posts/{post_id}/detail")
    assert r.status_code == 200


def test_get_draft_post_by_owner(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    r = client.get(f"/posts/{post_id}/detail", headers=auth_headers)
    assert r.status_code == 200


def test_get_draft_post_by_non_owner(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    other_headers = _second_user(client)
    r = client.get(f"/posts/{post_id}/detail", headers=other_headers)
    assert r.status_code == 403


def test_get_post_not_found(client):
    r = client.get("/posts/00000000-0000-0000-0000-000000000000/detail")
    assert r.status_code == 404


# ── Update ─────────────────────────────────────────────────────────────────

def test_update_post_success(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    r = client.put(
        f"/posts/{post_id}",
        json={"title": "Updated Title", "content": "Updated content."},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"


def test_update_post_forbidden(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    other_headers = _second_user(client)
    r = client.put(
        f"/posts/{post_id}",
        json={"title": "Hacked"},
        headers=other_headers,
    )
    assert r.status_code == 403


# ── Delete ─────────────────────────────────────────────────────────────────

def test_delete_post_success(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    r = client.delete(f"/posts/{post_id}", headers=auth_headers)
    assert r.status_code == 204
    # Confirm soft-delete: list should still show 0 published
    r2 = client.get("/posts")
    assert r2.json()["total"] == 0


def test_delete_post_forbidden(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    other_headers = _second_user(client)
    r = client.delete(f"/posts/{post_id}", headers=other_headers)
    assert r.status_code == 403


# ── Publish ────────────────────────────────────────────────────────────────

def test_publish_post_success(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    r = client.patch(f"/posts/{post_id}/publish", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None


def test_publish_already_published(client, auth_headers):
    resp = _create_post(client, auth_headers, status="published")
    post_id = resp.json()["id"]
    r = client.patch(f"/posts/{post_id}/publish", headers=auth_headers)
    assert r.status_code == 400
    assert "already published" in r.json()["detail"].lower()


def test_publish_forbidden(client, auth_headers):
    resp = _create_post(client, auth_headers)
    post_id = resp.json()["id"]
    other_headers = _second_user(client)
    r = client.patch(f"/posts/{post_id}/publish", headers=other_headers)
    assert r.status_code == 403


def test_slug_by_title(client, auth_headers):
    resp = _create_post(client, auth_headers, title="Hello World")
    slug = resp.json()["slug"]
    assert "hello" in slug
    assert "world" in slug

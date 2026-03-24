"""Tests for the Posts module — TDD first."""
import uuid
import pytest
from httpx import AsyncClient

from app.modules.auth.models import User
from app.modules.posts.models import Post
from app.modules.posts.service import generate_unique_slug
from sqlalchemy.ext.asyncio import AsyncSession


# ──────────────────────────────────────────────
# Slug generation tests
# ──────────────────────────────────────────────

async def test_slug_generation_basic(db_session: AsyncSession):
    slug = await generate_unique_slug(db_session, "Hello World")
    assert slug == "hello-world"


async def test_slug_generation_special_chars(db_session: AsyncSession):
    slug = await generate_unique_slug(db_session, "C++ is Great! @#$")
    assert "c" in slug
    assert " " not in slug
    assert "@" not in slug


async def test_slug_generation_unicode(db_session: AsyncSession):
    slug = await generate_unique_slug(db_session, "Café au lait")
    assert isinstance(slug, str)
    assert len(slug) > 0


# ──────────────────────────────────────────────
# Post CRUD API tests
# ──────────────────────────────────────────────

async def test_create_post_success(client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "My First Post",
        "content": "This is the content of my first blog post.",
        "tags": ["python", "fastapi"],
    }
    resp = await client.post("/posts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My First Post"
    assert data["slug"] == "my-first-post"
    assert data["status"] == "draft"
    assert "python" in data["tags"]
    assert "fastapi" in data["tags"]
    assert "id" in data
    assert "author_id" in data


async def test_create_post_with_all_fields(client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Full Post",
        "content": "Full content here.",
        "tags": ["seo", "blog"],
        "status": "draft",
        "summary": "Short summary",
        "seo_title": "SEO Title",
        "seo_description": "SEO description here",
    }
    resp = await client.post("/posts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["summary"] == "Short summary"
    assert data["seo_title"] == "SEO Title"
    assert data["seo_description"] == "SEO description here"


async def test_create_post_unauthenticated(client: AsyncClient):
    payload = {"title": "Unauthorized", "content": "Should fail"}
    resp = await client.post("/posts", json=payload)
    assert resp.status_code == 401


async def test_create_post_missing_title(client: AsyncClient, auth_headers: dict):
    payload = {"content": "No title here"}
    resp = await client.post("/posts", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_post_missing_content(client: AsyncClient, auth_headers: dict):
    payload = {"title": "No content here"}
    resp = await client.post("/posts", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_post_published_immediately(client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Published Post Direct",
        "content": "Content for published post.",
        "status": "published",
    }
    resp = await client.post("/posts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None


async def test_list_posts_empty(client: AsyncClient):
    resp = await client.get("/posts")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data


async def test_list_posts_only_published(client: AsyncClient, auth_headers: dict):
    # Create a draft post
    await client.post("/posts", json={"title": "Draft post", "content": "Content"}, headers=auth_headers)
    # Create a published post
    resp = await client.post("/posts", json={
        "title": "Public post for listing",
        "content": "Content",
        "status": "published"
    }, headers=auth_headers)
    assert resp.status_code == 201
    pub_id = resp.json()["id"]

    # List should only return published
    list_resp = await client.get("/posts")
    assert list_resp.status_code == 200
    slugs = [p["slug"] for p in list_resp.json()["items"]]
    assert any("public-post-for-listing" in s for s in slugs)


async def test_get_post_by_id(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Get by ID test",
        "content": "Content",
        "status": "published"
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    get_resp = await client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == post_id


async def test_get_post_by_slug(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Get by Slug Test Post",
        "content": "Content",
        "status": "published"
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    slug = create_resp.json()["slug"]

    get_resp = await client.get(f"/posts/{slug}")
    assert get_resp.status_code == 200
    assert get_resp.json()["slug"] == slug


async def test_get_draft_post_requires_auth(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Private Draft",
        "content": "Content"
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    # Unauthenticated should get 403
    get_resp = await client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 403


async def test_get_nonexistent_post(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/posts/{fake_id}")
    assert resp.status_code == 404


async def test_update_post(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Original Title",
        "content": "Original content",
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    update_resp = await client.put(f"/posts/{post_id}", json={
        "title": "Updated Title",
        "content": "Updated content",
    }, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Title"
    assert update_resp.json()["content"] == "Updated content"


async def test_update_post_tags(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Post with tags update",
        "content": "Content",
        "tags": ["old-tag"],
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    update_resp = await client.put(f"/posts/{post_id}", json={
        "tags": ["new-tag", "another-tag"],
    }, headers=auth_headers)
    assert update_resp.status_code == 200
    assert "new-tag" in update_resp.json()["tags"]
    assert "another-tag" in update_resp.json()["tags"]


async def test_update_post_wrong_owner(client: AsyncClient, auth_headers: dict, auth_headers2: dict):
    create_resp = await client.post("/posts", json={
        "title": "Owned post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    update_resp = await client.put(f"/posts/{post_id}", json={
        "title": "Hijacked title"
    }, headers=auth_headers2)
    assert update_resp.status_code == 403


async def test_update_post_unauthenticated(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Some post", "content": "Content"
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    resp = await client.put(f"/posts/{post_id}", json={"title": "New"})
    assert resp.status_code == 401


async def test_delete_post(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Post to delete",
        "content": "Content"
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/posts/{post_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    # Get should return 404 now
    get_resp = await client.get(f"/posts/{post_id}", headers=auth_headers)
    assert get_resp.status_code == 404


async def test_delete_post_wrong_owner(client: AsyncClient, auth_headers: dict, auth_headers2: dict):
    create_resp = await client.post("/posts", json={
        "title": "Protected post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/posts/{post_id}", headers=auth_headers2)
    assert del_resp.status_code == 403


async def test_publish_post(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Draft to Publish",
        "content": "Content"
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "draft"

    pub_resp = await client.patch(f"/posts/{post_id}/publish", headers=auth_headers)
    assert pub_resp.status_code == 200
    data = pub_resp.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None
    assert data["slug"] is not None


async def test_publish_already_published(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/posts", json={
        "title": "Already published post",
        "content": "Content",
        "status": "published",
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    pub_resp = await client.patch(f"/posts/{post_id}/publish", headers=auth_headers)
    assert pub_resp.status_code == 400
    assert "already published" in pub_resp.json()["detail"]


async def test_publish_wrong_owner(client: AsyncClient, auth_headers: dict, auth_headers2: dict):
    create_resp = await client.post("/posts", json={
        "title": "Another protected post",
        "content": "Content"
    }, headers=auth_headers)
    post_id = create_resp.json()["id"]

    pub_resp = await client.patch(f"/posts/{post_id}/publish", headers=auth_headers2)
    assert pub_resp.status_code == 403


async def test_list_posts_pagination(client: AsyncClient, auth_headers: dict):
    # Create 3 published posts
    for i in range(3):
        await client.post("/posts", json={
            "title": f"Paginated Post {uuid.uuid4().hex[:6]}",
            "content": "Content",
            "status": "published"
        }, headers=auth_headers)

    resp = await client.get("/posts?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


async def test_list_posts_filter_by_tag(client: AsyncClient, auth_headers: dict):
    tag = f"unique-tag-{uuid.uuid4().hex[:6]}"
    await client.post("/posts", json={
        "title": f"Tagged post {uuid.uuid4().hex[:6]}",
        "content": "Content",
        "tags": [tag],
        "status": "published"
    }, headers=auth_headers)

    resp = await client.get(f"/posts?tag={tag}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert tag in item["tags"]

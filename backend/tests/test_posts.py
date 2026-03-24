import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.posts.service import (
    create_post, get_post_by_id_or_slug, list_posts,
    update_post, delete_post, publish_post, _generate_slug,
)
from app.modules.posts.schemas import PostCreateRequest, PostUpdateRequest, PostStatus


class TestSlugGeneration:
    def test_basic_slug(self):
        assert _generate_slug("Hello World") == "hello-world"

    def test_slug_with_special_chars(self):
        slug = _generate_slug("What's new in Python?")
        assert " " not in slug
        assert slug

    def test_empty_title_gives_untitled(self):
        assert _generate_slug("") == "untitled"

    def test_slug_lowercase(self):
        slug = _generate_slug("UPPER CASE TITLE")
        assert slug == slug.lower()

    def test_slug_no_spaces(self):
        slug = _generate_slug("Hello World Again")
        assert " " not in slug
        assert "-" in slug


@pytest.mark.asyncio
async def test_create_post_draft(db_session: AsyncSession, test_user: User):
    data = PostCreateRequest(title="My First Post", content="Content.", status=PostStatus.draft)
    post = await create_post(db_session, data, test_user.id)
    assert post.title == "My First Post"
    assert post.slug == "my-first-post"
    assert post.status == "draft"
    assert post.author_id == test_user.id
    assert post.published_at is None


@pytest.mark.asyncio
async def test_create_post_published_sets_published_at(db_session: AsyncSession, test_user: User):
    data = PostCreateRequest(title="Published Post", content="Content.", status=PostStatus.published)
    post = await create_post(db_session, data, test_user.id)
    assert post.status == "published"
    assert post.published_at is not None


@pytest.mark.asyncio
async def test_create_post_with_tags(db_session: AsyncSession, test_user: User):
    data = PostCreateRequest(title="Tagged Post", content="Content.", tags=["python", "fastapi", "web"])
    post = await create_post(db_session, data, test_user.id)
    tag_names = [t.name for t in post.tags]
    assert "python" in tag_names
    assert "fastapi" in tag_names


@pytest.mark.asyncio
async def test_slug_collision_creates_unique_slug(db_session: AsyncSession, test_user: User):
    post1 = await create_post(db_session, PostCreateRequest(title="Same Title", content="C1."), test_user.id)
    post2 = await create_post(db_session, PostCreateRequest(title="Same Title", content="C2."), test_user.id)
    assert post1.slug != post2.slug
    assert post2.slug.startswith("same-title-")


@pytest.mark.asyncio
async def test_get_post_by_id(db_session: AsyncSession, test_user: User):
    post = await create_post(db_session, PostCreateRequest(title="Find By ID", content="C."), test_user.id)
    found = await get_post_by_id_or_slug(db_session, str(post.id))
    assert found is not None and found.id == post.id


@pytest.mark.asyncio
async def test_get_post_by_slug(db_session: AsyncSession, test_user: User):
    post = await create_post(db_session, PostCreateRequest(title="Find By Slug", content="C."), test_user.id)
    found = await get_post_by_id_or_slug(db_session, post.slug)
    assert found is not None and found.slug == post.slug


@pytest.mark.asyncio
async def test_get_post_not_found_returns_none(db_session: AsyncSession):
    assert await get_post_by_id_or_slug(db_session, "nonexistent-slug") is None


@pytest.mark.asyncio
async def test_update_post_content(db_session: AsyncSession, test_user: User):
    post = await create_post(db_session, PostCreateRequest(title="Update Me", content="Old."), test_user.id)
    updated = await update_post(db_session, post, PostUpdateRequest(content="New content updated."))
    assert updated.content == "New content updated."


@pytest.mark.asyncio
async def test_soft_delete_post(db_session: AsyncSession, test_user: User):
    post = await create_post(db_session, PostCreateRequest(title="Delete Me", content="C."), test_user.id)
    post_id = post.id
    await delete_post(db_session, post)
    assert post.deleted_at is not None
    assert await get_post_by_id_or_slug(db_session, str(post_id)) is None


@pytest.mark.asyncio
async def test_publish_post(db_session: AsyncSession, test_user: User):
    post = await create_post(db_session, PostCreateRequest(title="Publish Me", content="C."), test_user.id)
    published = await publish_post(db_session, post)
    assert published.status == "published"
    assert published.published_at is not None


@pytest.mark.asyncio
async def test_list_posts_only_published(db_session: AsyncSession, test_user: User):
    await create_post(db_session, PostCreateRequest(title="Draft Post", content="C.", status=PostStatus.draft), test_user.id)
    await create_post(db_session, PostCreateRequest(title="Pub Post", content="C.", status=PostStatus.published), test_user.id)
    posts, _ = await list_posts(db_session)
    slugs = [p.slug for p in posts]
    assert "pub-post" in slugs
    assert "draft-post" not in slugs


@pytest.mark.asyncio
async def test_api_create_post(client: AsyncClient, auth_headers: dict):
    response = await client.post("/posts", json={
        "title": "API Post", "content": "Some markdown content.", "tags": ["test", "api"]},
        headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Post"
    assert data["slug"] == "api-post"
    assert "test" in data["tags"]


@pytest.mark.asyncio
async def test_api_create_post_requires_auth(client: AsyncClient):
    response = await client.post("/posts", json={"title": "Unauthorized", "content": "C."})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_api_list_posts_public(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "List Test", "content": "C.", "status": "published"}, headers=auth_headers)
    post_id = resp.json()["id"]
    response = await client.get("/posts")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["items"]]
    assert post_id in ids


@pytest.mark.asyncio
async def test_api_get_published_post_public(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "Public Post", "content": "C.", "status": "published"}, headers=auth_headers)
    slug = resp.json()["slug"]
    response = await client.get(f"/posts/{slug}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_get_draft_requires_auth(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "Draft Hidden", "content": "C."}, headers=auth_headers)
    post_id = resp.json()["id"]
    response = await client.get(f"/posts/{post_id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_api_update_post(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "Before Update", "content": "Old."}, headers=auth_headers)
    post_id = resp.json()["id"]
    update_resp = await client.put(f"/posts/{post_id}", json={"title": "After Update", "content": "New."}, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "After Update"


@pytest.mark.asyncio
async def test_api_update_post_other_user_forbidden(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "User1 Post", "content": "C."}, headers=auth_headers)
    post_id = resp.json()["id"]
    await client.post("/auth/signup", json={"email": "user2@example.com", "password": "password123", "display_name": "User 2"})
    login_resp = await client.post("/auth/login", json={"email": "user2@example.com", "password": "password123"})
    u2_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
    response = await client.put(f"/posts/{post_id}", json={"title": "Hijacked"}, headers=u2_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_api_delete_post(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "To Delete", "content": "C."}, headers=auth_headers)
    post_id = resp.json()["id"]
    assert (await client.delete(f"/posts/{post_id}", headers=auth_headers)).status_code == 204
    assert (await client.get(f"/posts/{post_id}", headers=auth_headers)).status_code == 404


@pytest.mark.asyncio
async def test_api_publish_post(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "Publish Me", "content": "C."}, headers=auth_headers)
    pub_resp = await client.patch(f"/posts/{resp.json()['id']}/publish", headers=auth_headers)
    assert pub_resp.status_code == 200
    assert pub_resp.json()["status"] == "published"


@pytest.mark.asyncio
async def test_api_publish_already_published(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/posts", json={"title": "Already Published", "content": "C.", "status": "published"}, headers=auth_headers)
    pub_resp = await client.patch(f"/posts/{resp.json()['id']}/publish", headers=auth_headers)
    assert pub_resp.status_code == 400


@pytest.mark.asyncio
async def test_api_list_posts_pagination(client: AsyncClient, auth_headers: dict):
    for i in range(3):
        await client.post("/posts", json={"title": f"Paged {i}", "content": "C.", "status": "published"}, headers=auth_headers)
    response = await client.get("/posts?page=1&page_size=2")
    assert response.status_code == 200
    assert len(response.json()["items"]) <= 2


@pytest.mark.asyncio
async def test_api_list_posts_filter_by_tag(client: AsyncClient, auth_headers: dict):
    await client.post("/posts", json={"title": "Python Post", "content": "C.", "tags": ["python-unique-tag"], "status": "published"}, headers=auth_headers)
    await client.post("/posts", json={"title": "Go Post", "content": "C.", "tags": ["golang-unique-tag"], "status": "published"}, headers=auth_headers)
    response = await client.get("/posts?tag=python-unique-tag")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert "python-unique-tag" in item["tags"]

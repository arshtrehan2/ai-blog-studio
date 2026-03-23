import pytest


def _create_post(client, auth_headers, **overrides):
    payload = {
        "title": "My Test Post",
        "content": "This is the body of my test blog post.",
        "tags": ["python", "testing"],
        "status": "draft",
    }
    payload.update(overrides)
    return client.post("/posts", json=payload, headers=auth_headers)


def test_create_post_success(client, auth_headers):
    response = _create_post(client, auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Test Post"
    assert "slug" in data
    assert data["status"] == "draft"
    assert "python" in data["tags"]
    assert "testing" in data["tags"]
    assert "id" in data


def test_create_post_unauthenticated(client):
    response = client.post(
        "/posts",
        json={"title": "Test", "content": "Content"},
    )
    assert response.status_code == 403


def test_create_post_with_seo(client, auth_headers):
    response = _create_post(
        client,
        auth_headers,
        seo_title="SEO Title Here",
        seo_description="SEO description text.",
    )
    assert response.status_code == 201
    data = response.json()
    assert data["seo_title"] == "SEO Title Here"
    assert data["seo_description"] == "SEO description text."


def test_list_posts_public(client, auth_headers):
    # Create and publish a post
    post = _create_post(client, auth_headers).json()
    client.patch(f"/posts/{post['id']}/publish", headers=auth_headers)

    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 1


def test_list_posts_pagination(client, auth_headers):
    # Create multiple posts
    for i in range(3):
        p = _create_post(client, auth_headers, title=f"Post {i}").json()
        client.patch(f"/posts/{p['id']}/publish", headers=auth_headers)

    response = client.get("/posts?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["page_size"] == 2


def test_list_posts_filter_by_tag(client, auth_headers):
    p1 = _create_post(client, auth_headers, tags=["unique-tag-xyz"]).json()
    client.patch(f"/posts/{p1['id']}/publish", headers=auth_headers)
    p2 = _create_post(client, auth_headers, tags=["other-tag"]).json()
    client.patch(f"/posts/{p2['id']}/publish", headers=auth_headers)

    response = client.get("/posts?tag=unique-tag-xyz")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["tags"] == ["unique-tag-xyz"]


def test_get_published_post_by_id(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    client.patch(f"/posts/{post['id']}/publish", headers=auth_headers)

    response = client.get(f"/posts/{post['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == post["id"]


def test_get_published_post_by_slug(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    client.patch(f"/posts/{post['id']}/publish", headers=auth_headers)
    slug = post["slug"]

    response = client.get(f"/posts/{slug}")
    assert response.status_code == 200
    assert response.json()["slug"] == slug


def test_get_draft_post_requires_auth(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    # Unauthenticated access to draft should be 403
    response = client.get(f"/posts/{post['id']}")
    assert response.status_code == 403


def test_get_post_not_found(client):
    response = client.get("/posts/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_post_success(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    response = client.put(
        f"/posts/{post['id']}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_post_forbidden_other_user(client, db):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import get_db

    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        r1 = c.post(
            "/auth/signup",
            json={"email": "owner@ex.com", "password": "pass123456", "display_name": "Owner"},
        )
        r2 = c.post(
            "/auth/signup",
            json={"email": "intruder@ex.com", "password": "pass123456", "display_name": "Intruder"},
        )
        h1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

        post = c.post(
            "/posts",
            json={"title": "Owner post", "content": "Content"},
            headers=h1,
        ).json()
        response = c.put(
            f"/posts/{post['id']}",
            json={"title": "Hacked"},
            headers=h2,
        )
        assert response.status_code == 403
    app.dependency_overrides.clear()


def test_delete_post_success(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    response = client.delete(f"/posts/{post['id']}", headers=auth_headers)
    assert response.status_code == 204
    # Confirm it's gone
    get_response = client.get(f"/posts/{post['id']}", headers=auth_headers)
    assert get_response.status_code == 404


def test_publish_post_success(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    response = client.patch(f"/posts/{post['id']}/publish", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert "published_at" in data
    assert data["slug"] == post["slug"]


def test_publish_already_published(client, auth_headers):
    post = _create_post(client, auth_headers).json()
    client.patch(f"/posts/{post['id']}/publish", headers=auth_headers)
    response = client.patch(f"/posts/{post['id']}/publish", headers=auth_headers)
    assert response.status_code == 400
    assert "already published" in response.json()["detail"]


def test_slug_uniqueness(client, auth_headers):
    r1 = _create_post(client, auth_headers, title="Same Title")
    r2 = _create_post(client, auth_headers, title="Same Title")
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["slug"] != r2.json()["slug"]

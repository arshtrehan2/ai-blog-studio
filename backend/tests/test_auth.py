import pytest
from httpx import AsyncClient

from app.modules.auth.service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    create_refresh_token,
)


class TestPasswordHashing:
    def test_hash_password_produces_different_hash_each_time(self):
        h1 = hash_password("mysecret")
        h2 = hash_password("mysecret")
        assert h1 != h2

    def test_verify_password_correct(self):
        h = hash_password("mysecret")
        assert verify_password("mysecret", h) is True

    def test_verify_password_wrong(self):
        h = hash_password("mysecret")
        assert verify_password("wrongpassword", h) is False


class TestJWT:
    def test_create_and_decode_access_token(self):
        token = create_access_token("user-123")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        token = create_refresh_token("user-123")
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_decode_invalid_token_returns_none(self):
        result = decode_token("not.a.valid.token")
        assert result is None

    def test_decode_tampered_token_returns_none(self):
        token = create_access_token("user-123")
        tampered = token[:-5] + "XXXXX"
        result = decode_token(tampered)
        assert result is None


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    response = await client.post("/auth/signup", json={
        "email": "newuser@example.com",
        "password": "securepassword",
        "display_name": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert "password_hash" not in data["user"]


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "securepassword", "display_name": "User"}
    await client.post("/auth/signup", json=payload)
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient):
    response = await client.post("/auth/signup", json={
        "email": "not-an-email", "password": "securepassword", "display_name": "User"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_short_password(client: AsyncClient):
    response = await client.post("/auth/signup", json={
        "email": "user@example.com", "password": "short", "display_name": "User"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_empty_display_name(client: AsyncClient):
    response = await client.post("/auth/signup", json={
        "email": "user2@example.com", "password": "securepassword", "display_name": "   "})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/auth/signup", json={
        "email": "login@example.com", "password": "securepassword", "display_name": "Login User"})
    response = await client.post("/auth/login", json={
        "email": "login@example.com", "password": "securepassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/signup", json={
        "email": "wrongpw@example.com", "password": "correctpassword", "display_name": "User"})
    response = await client.post("/auth/login", json={
        "email": "wrongpw@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "email": "nobody@example.com", "password": "somepassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, auth_headers: dict):
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "password_hash" not in response.json()


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    response = await client.get("/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    response = await client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    response = await client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    assert "Logged out" in response.json()["message"]

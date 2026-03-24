"""Tests for the Auth module — TDD first."""
import uuid
import pytest
from httpx import AsyncClient

from app.modules.auth.service import (
    hash_password, verify_password, create_access_token, decode_access_token,
)


# ──────────────────────────────────────────────
# Unit tests for password hashing and JWT
# ──────────────────────────────────────────────

def test_hash_password_is_hashed():
    raw = "mysecretpassword"
    hashed = hash_password(raw)
    assert hashed != raw
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    raw = "mysecretpassword"
    hashed = hash_password(raw)
    assert verify_password(raw, hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("correct_password")
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token_decodeable():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    assert isinstance(token, str)
    token_data = decode_access_token(token)
    assert token_data is not None
    assert token_data.user_id == str(user_id)


def test_decode_invalid_token_returns_none():
    result = decode_access_token("not.a.valid.token")
    assert result is None


def test_decode_tampered_token_returns_none():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    tampered = token[:-5] + "XXXXX"
    result = decode_access_token(tampered)
    assert result is None


# ──────────────────────────────────────────────
# Integration tests via HTTP client
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    payload = {
        "email": f"signup_{uuid.uuid4().hex[:8]}@example.com",
        "password": "strongpassword",
        "display_name": "New User",
    }
    resp = await client.post("/auth/signup", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["display_name"] == payload["display_name"]
    assert "id" in data["user"]


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "strongpassword", "display_name": "User"}
    await client.post("/auth/signup", json=payload)
    resp = await client.post("/auth/signup", json=payload)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient):
    payload = {
        "email": f"weak_{uuid.uuid4().hex[:8]}@example.com",
        "password": "short",
        "display_name": "User",
    }
    resp = await client.post("/auth/signup", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient):
    payload = {
        "email": "not-an-email",
        "password": "strongpassword",
        "display_name": "User",
    }
    resp = await client.post("/auth/signup", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    # First sign up
    await client.post("/auth/signup", json={
        "email": email, "password": "password123", "display_name": "Login Test"
    })
    # Then login
    resp = await client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    email = f"badpw_{uuid.uuid4().hex[:8]}@example.com"
    await client.post("/auth/signup", json={
        "email": email, "password": "correctpass", "display_name": "User"
    })
    resp = await client.post("/auth/login", json={"email": email, "password": "wrongpass"})
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/auth/login", json={
        "email": "nobody@example.com", "password": "somepassword"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, auth_headers: dict, test_user):
    resp = await client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == test_user.email
    assert data["display_name"] == test_user.display_name


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_authenticated(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/auth/logout", headers=auth_headers)
    assert resp.status_code == 200
    assert "Logged out" in resp.json()["message"]


@pytest.mark.asyncio
async def test_logout_unauthenticated(client: AsyncClient):
    resp = await client.post("/auth/logout")
    assert resp.status_code == 401

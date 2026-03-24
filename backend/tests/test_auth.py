"""
TDD tests for the Auth module.

Covers:
- POST /auth/signup  (201, 409, 422)
- POST /auth/login   (200, 401)
- POST /auth/logout  (200, 401)
- GET  /auth/me      (200, 401)
"""
import pytest


# ── Signup ─────────────────────────────────────────────────────────────────

def test_signup_success(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "password": "secret123", "display_name": "Alice"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["display_name"] == "Alice"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_signup_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "secret123", "display_name": "Dup"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"].lower()


def test_signup_short_password(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "short@example.com", "password": "abc", "display_name": "Short"},
    )
    assert resp.status_code == 422


def test_signup_invalid_email(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "not-an-email", "password": "password123", "display_name": "Bad"},
    )
    assert resp.status_code == 422


def test_signup_missing_display_name(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "nodisplay@example.com", "password": "password123"},
    )
    assert resp.status_code == 422


# ── Login ───────────────────────────────────────────────────────────────────

def test_login_success(client, registered_user):
    user, _ = registered_user
    resp = client.post(
        "/auth/login",
        json={"email": user["email"], "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == user["email"]


def test_login_wrong_password(client, registered_user):
    user, _ = registered_user
    resp = client.post(
        "/auth/login",
        json={"email": user["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert "invalid credentials" in resp.json()["detail"].lower()


def test_login_unknown_email(client):
    resp = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


# ── Me ─────────────────────────────────────────────────────────────────────

def test_me_authenticated(client, registered_user, auth_headers):
    user, _ = registered_user
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == user["email"]
    assert data["display_name"] == user["display_name"]


def test_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_invalid_token(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────

def test_logout_authenticated(client, auth_headers):
    resp = client.post("/auth/logout", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Logged out successfully"


def test_logout_unauthenticated(client):
    resp = client.post("/auth/logout")
    assert resp.status_code == 401

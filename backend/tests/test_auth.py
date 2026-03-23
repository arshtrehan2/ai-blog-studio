import pytest


def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "display_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["display_name"] == "New User"
    assert "id" in data["user"]
    assert "created_at" in data["user"]


def test_signup_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "securepass123",
        "display_name": "User",
    }
    client.post("/auth/signup", json=payload)
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 409
    assert "Email already registered" in response.json()["detail"]


def test_signup_invalid_email(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "not-an-email",
            "password": "securepass123",
            "display_name": "User",
        },
    )
    assert response.status_code == 422


def test_signup_short_password(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "short@example.com",
            "password": "short",
            "display_name": "User",
        },
    )
    assert response.status_code == 422


def test_login_success(client, test_user_data):
    client.post("/auth/signup", json=test_user_data)
    response = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user_data["email"]


def test_login_invalid_password(client, test_user_data):
    client.post("/auth/signup", json=test_user_data)
    response = client.post(
        "/auth/login",
        json={"email": test_user_data["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_get_me_success(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "display_name" in data


def test_get_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 403


def test_get_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


def test_logout_success(client, auth_headers):
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


def test_logout_unauthorized(client):
    response = client.post("/auth/logout")
    assert response.status_code == 403

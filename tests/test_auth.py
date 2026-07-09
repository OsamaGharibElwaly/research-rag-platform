"""Auth service tests."""
from backend.shared.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestHealth:
    def test_health_check(self, auth_client):
        response = auth_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth_service"


class TestRegistration:
    def test_register_success(self, auth_client):
        response = auth_client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["user"]["email"] == "new@example.com"
        assert "access_token" in data["data"]["tokens"]

    def test_register_duplicate_email(self, auth_client):
        auth_client.post(
            "/api/auth/register",
            json={
                "email": "dup@example.com",
                "username": "user1",
                "password": "password123",
            },
        )
        response = auth_client.post(
            "/api/auth/register",
            json={
                "email": "dup@example.com",
                "username": "user2",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    def test_register_duplicate_username(self, auth_client):
        auth_client.post(
            "/api/auth/register",
            json={
                "email": "a@example.com",
                "username": "sameuser",
                "password": "password123",
            },
        )
        response = auth_client.post(
            "/api/auth/register",
            json={
                "email": "b@example.com",
                "username": "sameuser",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    def test_register_invalid_email(self, auth_client):
        response = auth_client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "username": "newuser",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_register_short_password(self, auth_client):
        response = auth_client.post(
            "/api/auth/register",
            json={
                "email": "short@example.com",
                "username": "newuser",
                "password": "123",
            },
        )
        assert response.status_code == 422


class TestPasswordHashing:
    def test_password_hashing(self):
        hashed = get_password_hash("password123")
        assert hashed != "password123"
        assert verify_password("password123", hashed)
        assert not verify_password("wrongpassword", hashed)


class TestLogin:
    def test_login_success(self, auth_client):
        auth_client.post(
            "/api/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123",
            },
        )
        response = auth_client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_login_invalid_password(self, auth_client):
        auth_client.post(
            "/api/auth/register",
            json={
                "email": "wrongpw@example.com",
                "username": "wrongpwuser",
                "password": "password123",
            },
        )
        response = auth_client.post(
            "/api/auth/login",
            json={"email": "wrongpw@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, auth_client):
        response = auth_client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401


class TestJWT:
    def test_jwt_creation_and_verification(self):
        token = create_access_token({"sub": "1", "email": "test@example.com"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["type"] == "access"

    def test_invalid_token(self):
        assert decode_token("invalid.token.here") is None

    def test_expired_token(self):
        from datetime import timedelta

        token = create_access_token(
            {"sub": "1", "email": "test@example.com"},
            expires_delta=timedelta(seconds=-1),
        )
        assert decode_token(token) is None


class TestTokenRefresh:
    def test_refresh_token_success(self, auth_client):
        auth_client.post(
            "/api/auth/register",
            json={
                "email": "refresh@example.com",
                "username": "refreshuser",
                "password": "password123",
            },
        )
        login_response = auth_client.post(
            "/api/auth/login",
            json={"email": "refresh@example.com", "password": "password123"},
        )
        refresh_token = login_response.json()["data"]["tokens"]["refresh_token"]

        response = auth_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()["data"]

    def test_refresh_invalid_token(self, auth_client):
        response = auth_client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code == 401

    def test_refresh_with_access_token_rejected(self, auth_client):
        token = create_access_token({"sub": "1", "email": "test@example.com"})
        response = auth_client.post(
            "/api/auth/refresh",
            json={"refresh_token": token},
        )
        assert response.status_code == 401


class TestGetMe:
    def test_get_me_success(self, auth_client, auth_headers):
        response = auth_client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["user"]["email"] == "test@example.com"

    def test_get_me_no_token(self, auth_client):
        response = auth_client.get("/api/auth/me")
        assert response.status_code in (401, 403)

    def test_get_me_invalid_token(self, auth_client):
        response = auth_client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_get_me_with_refresh_token_rejected(self, auth_client):
        refresh = create_refresh_token({"sub": "1", "email": "test@example.com"})
        response = auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {refresh}"},
        )
        assert response.status_code == 401

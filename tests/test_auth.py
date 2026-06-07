import pytest
from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/auth/register", json={
            "full_name": "John Doe",
            "username": "johndoe",
            "phone_number": "08123456789",
            "email": "john@example.com",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "johndoe"
        assert data["data"]["email"] == "john@example.com"

    async def test_register_duplicate_username(self, client: AsyncClient):
        payload = {
            "full_name": "John Doe",
            "username": "johndoe",
            "phone_number": "08123456789",
            "email": "john@example.com",
            "password": "password123",
        }
        await client.post("/auth/register", json=payload)

        payload["email"] = "different@example.com"
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 409
        assert response.json()["error_code"] == "USERNAME_EXISTS"

    async def test_register_duplicate_email(self, client: AsyncClient):
        payload = {
            "full_name": "John Doe",
            "username": "johndoe",
            "phone_number": "08123456789",
            "email": "john@example.com",
            "password": "password123",
        }
        await client.post("/auth/register", json=payload)

        payload["username"] = "different"
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 409
        assert response.json()["error_code"] == "EMAIL_EXISTS"

    async def test_register_missing_fields(self, client: AsyncClient):
        response = await client.post("/auth/register", json={
            "username": "johndoe",
        })
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, registered_user):
        response = await client.post("/auth/login", json={
            "username": "testuser",
            "password": "securepassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        response = await client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword",
        })
        assert response.status_code == 401
        assert response.json()["error_code"] == "INVALID_CREDENTIALS"

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/auth/login", json={
            "username": "noone",
            "password": "password123",
        })
        assert response.status_code == 401
        assert response.json()["error_code"] == "INVALID_CREDENTIALS"


class TestMe:
    async def test_get_me_authenticated(self, client: AsyncClient, auth_token):
        response = await client.get("/auth/me", headers=auth_token)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "testuser"

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/auth/me")
        assert response.status_code == 401

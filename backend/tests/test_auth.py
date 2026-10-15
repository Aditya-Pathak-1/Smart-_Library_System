import pytest
from httpx import AsyncClient


class TestAuth:
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "password123",
            "full_name": "New User",
            "role": "member"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["full_name"] == "New User"
        assert data["role"] == "member"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, admin_user):
        response = await client.post("/api/v1/auth/register", json={
            "email": "admin@test.com",
            "password": "password123",
            "full_name": "Duplicate User",
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, admin_user):
        response = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, admin_user):
        response = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_admin_can_temporarily_impersonate_member(
        self, client: AsyncClient, admin_token, member_user
    ):
        response = await client.post(
            f"/api/v1/auth/impersonate/{member_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        tokens = response.json()

        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == member_user.id
        assert me_response.json()["role"] == "member"

        admin_only_response = await client.get(
            "/api/v1/auth/users",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert admin_only_response.status_code == 403

        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_cannot_impersonate_another_admin(
        self, client: AsyncClient, admin_token, admin_user
    ):
        response = await client.post(
            f"/api/v1/auth/impersonate/{admin_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, admin_token, admin_user):
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
import pytest
from httpx import AsyncClient
from datetime import date, timedelta


class TestMembers:
    @pytest.mark.asyncio
    async def test_create_member(self, client: AsyncClient, librarian_token):
        response = await client.post(
            "/api/v1/members",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@test.com",
                "phone": "+91-9876543210",
                "membership_type": "standard",
                "registration_date": date.today().isoformat(),
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["member_id"].startswith("MEM")

    @pytest.mark.asyncio
    async def test_create_duplicate_email(self, client: AsyncClient, librarian_token, test_member):
        response = await client.post(
            "/api/v1/members",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": test_member.email,
                "registration_date": date.today().isoformat(),
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_members(self, client: AsyncClient, librarian_token, test_member):
        response = await client.get(
            "/api/v1/members",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_search_members(self, client: AsyncClient, librarian_token, test_member):
        response = await client.get(
            "/api/v1/members",
            params={"search": test_member.first_name[:3]},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_member(self, client: AsyncClient, librarian_token, test_member):
        response = await client.get(
            f"/api/v1/members/{test_member.id}",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_member.id

    @pytest.mark.asyncio
    async def test_get_member_detail(self, client: AsyncClient, librarian_token, test_member):
        response = await client.get(
            f"/api/v1/members/{test_member.id}",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "currently_issued_books" in data
        assert "total_books_borrowed" in data

    @pytest.mark.asyncio
    async def test_update_member(self, client: AsyncClient, librarian_token, test_member):
        response = await client.patch(
            f"/api/v1/members/{test_member.id}",
            json={"phone": "+91-9999999999"},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+91-9999999999"

    @pytest.mark.asyncio
    async def test_member_stats(self, client: AsyncClient, librarian_token):
        response = await client.get(
            "/api/v1/members/stats",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "active" in data


class TestMemberProfile:
    @pytest.mark.asyncio
    async def test_get_my_profile(self, client: AsyncClient, member_token, test_member):
        response = await client.get(
            "/api/v1/members/profile",
            headers={"Authorization": f"Bearer {member_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_member.email

    @pytest.mark.asyncio
    async def test_get_my_history(self, client: AsyncClient, member_token):
        response = await client.get(
            "/api/v1/members/profile/history",
            headers={"Authorization": f"Bearer {member_token}"}
        )
        assert response.status_code == 200
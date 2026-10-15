import pytest
from httpx import AsyncClient
from datetime import date, timedelta


class TestReports:
    @pytest.mark.asyncio
    async def test_dashboard_stats(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/dashboard/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_books" in data
        assert "available_books" in data
        assert "issued_books" in data
        assert "total_members" in data
        assert "overdue_books" in data

    @pytest.mark.asyncio
    async def test_issue_return_chart(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/dashboard/charts/issue-return",
            params={"days": 7},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "issues" in data
        assert "returns" in data
        assert len(data["labels"]) == 7

    @pytest.mark.asyncio
    async def test_category_chart(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/dashboard/charts/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "values" in data

    @pytest.mark.asyncio
    async def test_recent_activity(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/dashboard/recent-activity",
            params={"limit": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_overdue_books(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/dashboard/overdue",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_inventory_report(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/inventory",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_issued_books_report(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/issued",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_overdue_books_report(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/overdue",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_member_activity_report(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/members",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_fine_collection_report(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/fines",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_most_borrowed_books(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/most-borrowed",
            params={"limit": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_export_inventory_csv(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/inventory/export",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        content = response.text
        assert "Book ID,Title,ISBN" in content

    @pytest.mark.asyncio
    async def test_export_issued_csv(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/reports/reports/issued/export",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
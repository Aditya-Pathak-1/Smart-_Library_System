import pytest
from httpx import AsyncClient


class TestCategories:
    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient, admin_token):
        response = await client.post(
            "/api/v1/books/categories",
            json={"name": "New Category", "description": "Description"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"

    @pytest.mark.asyncio
    async def test_create_duplicate_category(self, client: AsyncClient, admin_token, test_category):
        response = await client.post(
            "/api/v1/books/categories",
            json={"name": test_category.name, "description": "Description"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_categories(self, client: AsyncClient, admin_token, test_category):
        response = await client.get(
            "/api/v1/books/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_category(self, client: AsyncClient, admin_token, test_category):
        response = await client.get(
            f"/api/v1/books/categories/{test_category.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id

    @pytest.mark.asyncio
    async def test_update_category(self, client: AsyncClient, admin_token, test_category):
        response = await client.patch(
            f"/api/v1/books/categories/{test_category.id}",
            json={"name": "Updated Category"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category"

    @pytest.mark.asyncio
    async def test_delete_category(self, client: AsyncClient, admin_token):
        response = await client.post(
            "/api/v1/books/categories",
            json={"name": "To Delete"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        cat_id = response.json()["id"]
        
        response = await client.delete(
            f"/api/v1/books/categories/{cat_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204


class TestAuthors:
    @pytest.mark.asyncio
    async def test_create_author(self, client: AsyncClient, admin_token):
        response = await client.post(
            "/api/v1/books/authors",
            json={"name": "New Author", "biography": "Bio", "nationality": "Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Author"

    @pytest.mark.asyncio
    async def test_list_authors(self, client: AsyncClient, admin_token, test_author):
        response = await client.get(
            "/api/v1/books/authors",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


class TestBooks:
    @pytest.mark.asyncio
    async def test_create_book(self, client: AsyncClient, admin_token, test_category, test_author):
        response = await client.post(
            "/api/v1/books",
            json={
                "title": "New Book",
                "isbn": "9780000000002",
                "author_id": test_author.id,
                "category_id": test_category.id,
                "total_copies": 3,
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Book"
        assert data["available_copies"] == 3
        assert data["total_copies"] == 3

    @pytest.mark.asyncio
    async def test_create_duplicate_isbn(self, client: AsyncClient, admin_token, test_book, test_category, test_author):
        response = await client.post(
            "/api/v1/books",
            json={
                "title": "Duplicate Book",
                "isbn": test_book.isbn,
                "author_id": test_author.id,
                "category_id": test_category.id,
                "total_copies": 1,
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_books(self, client: AsyncClient, admin_token, test_book):
        response = await client.get(
            "/api/v1/books",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_search_books(self, client: AsyncClient, admin_token, test_book):
        response = await client.get(
            "/api/v1/books",
            params={"search": test_book.title[:5]},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_search_books_by_category(self, client: AsyncClient, admin_token, test_book, test_category):
        response = await client.get(
            "/api/v1/books",
            params={"search": test_category.name},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert any(book["id"] == test_book.id for book in response.json())

    @pytest.mark.asyncio
    async def test_filter_books_by_category(self, client: AsyncClient, admin_token, test_book, test_category):
        response = await client.get(
            "/api/v1/books",
            params={"category_id": test_category.id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(b["category_id"] == test_category.id for b in data)

    @pytest.mark.asyncio
    async def test_get_book(self, client: AsyncClient, admin_token, test_book):
        response = await client.get(
            f"/api/v1/books/{test_book.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_book.id

    @pytest.mark.asyncio
    async def test_update_book(self, client: AsyncClient, admin_token, test_book):
        response = await client.patch(
            f"/api/v1/books/{test_book.id}",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_book_copies(self, client: AsyncClient, admin_token, test_book):
        original_total = test_book.total_copies
        response = await client.patch(
            f"/api/v1/books/{test_book.id}",
            json={"total_copies": original_total + 2},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_copies"] == original_total + 2
        assert data["available_copies"] == test_book.available_copies + 2

    @pytest.mark.asyncio
    async def test_book_stats(self, client: AsyncClient, admin_token):
        response = await client.get(
            "/api/v1/books/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_titles" in data
        assert "total_copies" in data
        assert "available_copies" in data


class TestBookCopies:
    @pytest.mark.asyncio
    async def test_list_copies(self, client: AsyncClient, admin_token, test_book):
        response = await client.get(
            f"/api/v1/books/{test_book.id}/copies",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == test_book.total_copies

    @pytest.mark.asyncio
    async def test_create_copy(self, client: AsyncClient, admin_token, test_book):
        response = await client.post(
            f"/api/v1/books/{test_book.id}/copies",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["book_id"] == test_book.id
        assert data["copy_number"] == test_book.total_copies + 1
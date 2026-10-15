import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from sqlalchemy import delete, select

from app.models.book import BookCopy


class TestIssues:
    @pytest.mark.asyncio
    async def test_issue_book(self, client: AsyncClient, librarian_token, test_member, test_book):
        response = await client.post(
            "/api/v1/issues/issue",
            json={
                "member_id": test_member.id,
                "book_id": test_book.id,
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["member_id"] == test_member.id
        assert data["book_id"] == test_book.id
        assert data["status"] == "issued"
        assert data["transaction_id"].startswith("TXN")

        list_response = await client.get(
            "/api/v1/issues/transactions",
            headers={"Authorization": f"Bearer {librarian_token}"},
        )
        assert list_response.status_code == 200
        assert any(
            transaction["transaction_id"] == data["transaction_id"]
            for transaction in list_response.json()
        )

    @pytest.mark.asyncio
    async def test_issue_book_repairs_missing_copy_records(
        self, client: AsyncClient, librarian_token, test_member, test_book, db_session
    ):
        await db_session.execute(delete(BookCopy).where(BookCopy.book_id == test_book.id))
        await db_session.commit()

        response = await client.post(
            "/api/v1/issues/issue",
            json={"member_id": test_member.id, "book_id": test_book.id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 201, response.text

        copies_result = await db_session.execute(
            select(BookCopy).where(BookCopy.book_id == test_book.id)
        )
        copies = list(copies_result.scalars().all())
        assert len(copies) == 1
        assert copies[0].is_available is False

    @pytest.mark.parametrize("borrow_days", [7, 14, 30])
    @pytest.mark.asyncio
    async def test_issue_book_uses_selected_borrowing_period(
        self, client: AsyncClient, librarian_token, test_member, test_book, borrow_days
    ):
        response = await client.post(
            "/api/v1/issues/issue",
            json={
                "member_id": test_member.id,
                "book_id": test_book.id,
                "borrow_days": borrow_days,
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 201
        assert response.json()["due_date"] == (date.today() + timedelta(days=borrow_days)).isoformat()

    @pytest.mark.asyncio
    async def test_issue_due_today_is_not_overdue(
        self, client: AsyncClient, librarian_token, test_member, test_book
    ):
        issue_response = await client.post(
            "/api/v1/issues/issue",
            json={
                "member_id": test_member.id,
                "book_id": test_book.id,
                "due_date": date.today().isoformat(),
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert issue_response.status_code == 201

        detail_response = await client.get(
            f"/api/v1/issues/transactions/{issue_response.json()['transaction_id']}",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert detail_response.status_code == 200
        assert detail_response.json()["is_overdue"] is False
        assert detail_response.json()["overdue_days"] == 0

    @pytest.mark.asyncio
    async def test_issue_unavailable_book(self, client: AsyncClient, librarian_token, test_member, test_book, db_session):
        from app.models.book import Book
        book = await db_session.get(Book, test_book.id)
        book.available_copies = 0
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/issues/issue",
            json={
                "member_id": test_member.id,
                "book_id": test_book.id,
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_issue_inactive_member(self, client: AsyncClient, librarian_token, test_member, test_book, db_session):
        from app.models.member import Member, MembershipStatusEnum
        member = await db_session.get(Member, test_member.id)
        member.status = MembershipStatusEnum.INACTIVE
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/issues/issue",
            json={
                "member_id": test_member.id,
                "book_id": test_book.id,
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_return_book(self, client: AsyncClient, librarian_token, test_member, test_book):
        # First issue a book
        issue_response = await client.post(
            "/api/v1/issues/issue",
            json={"member_id": test_member.id, "book_id": test_book.id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        transaction_id = issue_response.json()["transaction_id"]
        
        # Now return it
        response = await client.post(
            "/api/v1/issues/return",
            json={"transaction_id": transaction_id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "returned"
        assert data["return_date"] is not None

    @pytest.mark.asyncio
    async def test_return_already_returned(self, client: AsyncClient, librarian_token, test_member, test_book):
        issue_response = await client.post(
            "/api/v1/issues/issue",
            json={"member_id": test_member.id, "book_id": test_book.id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        transaction_id = issue_response.json()["transaction_id"]
        
        await client.post(
            "/api/v1/issues/return",
            json={"transaction_id": transaction_id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        
        response = await client.post(
            "/api/v1/issues/return",
            json={"transaction_id": transaction_id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_renew_book(self, client: AsyncClient, librarian_token, test_member, test_book):
        issue_response = await client.post(
            "/api/v1/issues/issue",
            json={"member_id": test_member.id, "book_id": test_book.id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        transaction_id = issue_response.json()["transaction_id"]
        
        response = await client.post(
            f"/api/v1/issues/renew/{transaction_id}",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["renewed_count"] == 1

    @pytest.mark.asyncio
    async def test_list_transactions(self, client: AsyncClient, librarian_token):
        response = await client.get(
            "/api/v1/issues/transactions",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_filter_transactions_by_status(self, client: AsyncClient, librarian_token, test_member, test_book):
        await client.post(
            "/api/v1/issues/issue",
            json={"member_id": test_member.id, "book_id": test_book.id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        
        response = await client.get(
            "/api/v1/issues/transactions",
            params={"status": "issued"},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(t["status"] == "issued" for t in data)

    @pytest.mark.asyncio
    async def test_get_transaction_detail(self, client: AsyncClient, librarian_token, test_member, test_book):
        issue_response = await client.post(
            "/api/v1/issues/issue",
            json={"member_id": test_member.id, "book_id": test_book.id},
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        transaction_id = issue_response.json()["transaction_id"]
        
        response = await client.get(
            f"/api/v1/issues/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == transaction_id
        assert "is_overdue" in data
        assert "overdue_days" in data
        assert "estimated_fine" in data

    @pytest.mark.asyncio
    async def test_member_transactions(self, client: AsyncClient, librarian_token, test_member):
        response = await client.get(
            f"/api/v1/issues/member/{test_member.id}/transactions",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_issue_stats(self, client: AsyncClient, librarian_token):
        response = await client.get(
            "/api/v1/issues/transactions/stats",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "issued" in data
        assert "returned" in data
        assert "overdue" in data
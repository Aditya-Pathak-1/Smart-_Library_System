import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from decimal import Decimal


class TestFines:
    @pytest.mark.asyncio
    async def test_list_fines(self, client: AsyncClient, librarian_token):
        response = await client.get(
            "/api/v1/fines/fines",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_overdue_books_with_fines(self, client: AsyncClient, librarian_token, test_member, test_book, db_session):
        from app.models.issue import IssueTransaction, IssueStatusEnum
        from app.models.settings import LibrarySettings
        
        # Create an overdue transaction
        issue_date = date.today() - timedelta(days=20)
        due_date = date.today() - timedelta(days=5)
        
        transaction = IssueTransaction(
            transaction_id="TXNFINE001",
            member_id=test_member.id,
            book_id=test_book.id,
            issue_date=issue_date,
            due_date=due_date,
            status=IssueStatusEnum.ISSUED,
            issued_by=1,
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)
        
        response = await client.get(
            "/api/v1/fines/fines/overdue",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["transaction_id"] == "TXNFINE001"
        assert data[0]["overdue_days"] >= 5

    @pytest.mark.asyncio
    async def test_fine_stats(self, client: AsyncClient, librarian_token):
        response = await client.get(
            "/api/v1/fines/fines/stats",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_fines" in data
        assert "pending" in data
        assert "paid" in data
        assert "outstanding" in data

    @pytest.mark.asyncio
    async def test_record_payment(self, client: AsyncClient, librarian_token, test_member, test_book, db_session):
        from app.models.fine import Fine, FineStatusEnum
        from app.models.issue import IssueTransaction, IssueStatusEnum
        
        # Create an overdue transaction and fine
        issue_date = date.today() - timedelta(days=20)
        due_date = date.today() - timedelta(days=5)
        
        transaction = IssueTransaction(
            transaction_id="TXNPAY001",
            member_id=test_member.id,
            book_id=test_book.id,
            issue_date=issue_date,
            due_date=due_date,
            status=IssueStatusEnum.OVERDUE,
            issued_by=1,
            fine_amount=25.00,
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)
        
        fine = Fine(
            fine_id="FINEPAY001",
            member_id=test_member.id,
            issue_id=transaction.id,
            overdue_days=5,
            fine_per_day=Decimal("5.00"),
            calculated_amount=Decimal("25.00"),
            final_amount=Decimal("25.00"),
            status=FineStatusEnum.PENDING,
        )
        db_session.add(fine)
        await db_session.commit()
        await db_session.refresh(fine)
        
        response = await client.post(
            "/api/v1/fines/fines/pay",
            json={
                "fine_id": fine.id,
                "amount": "25.00",
                "payment_method": "cash",
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 25.00
        assert data["payment_method"] == "cash"
        assert data["receipt_number"].startswith("RCP")

    @pytest.mark.asyncio
    async def test_partial_payment(self, client: AsyncClient, librarian_token, test_member, test_book, db_session):
        from app.models.fine import Fine, FineStatusEnum
        from app.models.issue import IssueTransaction, IssueStatusEnum
        
        transaction = IssueTransaction(
            transaction_id="TXNPAY002",
            member_id=test_member.id,
            book_id=test_book.id,
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=5),
            status=IssueStatusEnum.OVERDUE,
            issued_by=1,
            fine_amount=50.00,
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)
        
        fine = Fine(
            fine_id="FINEPAY002",
            member_id=test_member.id,
            issue_id=transaction.id,
            overdue_days=10,
            fine_per_day=Decimal("5.00"),
            calculated_amount=Decimal("50.00"),
            final_amount=Decimal("50.00"),
            status=FineStatusEnum.PENDING,
        )
        db_session.add(fine)
        await db_session.commit()
        await db_session.refresh(fine)
        
        # Partial payment
        response = await client.post(
            "/api/v1/fines/fines/pay",
            json={
                "fine_id": fine.id,
                "amount": "20.00",
                "payment_method": "card",
            },
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 20.00
        
        # Check fine status is partial
        response = await client.get(
            f"/api/v1/fines/fines/{fine.id}",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "partial"
        assert data["paid_amount"] == 20.00
        assert data["outstanding_balance"] == 30.00

    @pytest.mark.asyncio
    async def test_member_fines_summary(self, client: AsyncClient, librarian_token, test_member):
        response = await client.get(
            f"/api/v1/fines/members/{test_member.id}/fines/summary",
            headers={"Authorization": f"Bearer {librarian_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_fines" in data
        assert "total_amount" in data
        assert "paid_amount" in data
        assert "outstanding" in data
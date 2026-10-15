from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.fine import Fine, FineStatusEnum, FinePayment
from app.models.issue import IssueTransaction, IssueStatusEnum
from app.models.member import Member
from app.models.settings import LibrarySettings
from app.schemas.fine import FineUpdate, FinePaymentCreate


class FineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_fine_id(self) -> str:
        import random
        import string
        return "FINE" + "".join(random.choices(string.digits, k=8))

    def _generate_payment_id(self) -> str:
        import random
        import string
        return "PAY" + "".join(random.choices(string.digits, k=8))

    def _generate_receipt_number(self) -> str:
        import random
        import string
        return "RCP" + "".join(random.choices(string.digits, k=10))

    async def create_fine_from_return(
        self, transaction: IssueTransaction, overdue_days: int, fine_per_day: Decimal
    ) -> Fine:
        chargeable_days = max(0, overdue_days)
        calculated_amount = Decimal(str(chargeable_days)) * fine_per_day

        fine = Fine(
            fine_id=self._generate_fine_id(),
            member_id=transaction.member_id,
            issue_id=transaction.id,
            overdue_days=chargeable_days,
            fine_per_day=fine_per_day,
            calculated_amount=calculated_amount,
            final_amount=calculated_amount,
            status=FineStatusEnum.PENDING if calculated_amount > 0 else FineStatusEnum.PAID,
            finalized_at=datetime.utcnow() if calculated_amount > 0 else None,
        )
        self.db.add(fine)

        # Update member outstanding fines
        member = await self.db.get(Member, transaction.member_id)
        if member:
            member.outstanding_fines += calculated_amount

        # Update transaction
        transaction.fine_amount = calculated_amount

        await self.db.commit()
        await self.db.refresh(fine)
        return fine

    async def get_fine(self, fine_id: int) -> Optional[Fine]:
        result = await self.db.execute(
            select(Fine)
            .options(selectinload(Fine.member), selectinload(Fine.issue).selectinload(IssueTransaction.book))
            .where(Fine.id == fine_id)
        )
        return result.scalar_one_or_none()

    async def get_fines(
        self,
        skip: int = 0,
        limit: int = 20,
        member_id: Optional[int] = None,
        status: Optional[FineStatusEnum] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Fine], int]:
        query = select(Fine).options(
            selectinload(Fine.member),
            selectinload(Fine.issue).selectinload(IssueTransaction.book),
        )

        if member_id:
            query = query.where(Fine.member_id == member_id)
        if status:
            query = query.where(Fine.status == status)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                Fine.fine_id.ilike(search_term) |
                Fine.member.has(Member.first_name.ilike(search_term)) |
                Fine.member.has(Member.last_name.ilike(search_term)) |
                Fine.issue.has(IssueTransaction.book.has(IssueTransaction.book.property.mapper.class_.title.ilike(search_term)))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        result = await self.db.execute(query.order_by(Fine.calculated_at.desc()).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def update_fine(self, fine_id: int, data: FineUpdate) -> Fine:
        fine = await self.get_fine(fine_id)
        if not fine:
            raise HTTPException(status_code=404, detail="Fine not found")

        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data:
            update_data["status"] = FineStatusEnum(update_data["status"])

        for field, value in update_data.items():
            setattr(fine, field, value)

        if "final_amount" in update_data and fine.final_amount != update_data["final_amount"]:
            diff = update_data["final_amount"] - fine.final_amount
            member = await self.db.get(Member, fine.member_id)
            if member:
                member.outstanding_fines = max(Decimal("0"), member.outstanding_fines + diff)

        await self.db.commit()
        await self.db.refresh(fine)
        return fine

    async def record_payment(self, data: FinePaymentCreate, received_by: int) -> FinePayment:
        fine = await self.get_fine(data.fine_id)
        if not fine:
            raise HTTPException(status_code=404, detail="Fine not found")

        if fine.status == FineStatusEnum.PAID:
            raise HTTPException(status_code=400, detail="Fine already paid")
        if fine.status == FineStatusEnum.WAIVED:
            raise HTTPException(status_code=400, detail="Fine has been waived")

        if data.amount > (fine.final_amount - fine.paid_amount):
            raise HTTPException(status_code=400, detail="Payment amount exceeds outstanding balance")

        payment = FinePayment(
            payment_id=self._generate_payment_id(),
            fine_id=data.fine_id,
            amount=data.amount,
            payment_method=data.payment_method,
            receipt_number=self._generate_receipt_number(),
            received_by=received_by,
            notes=data.notes,
        )
        self.db.add(payment)

        fine.paid_amount += data.amount
        if fine.paid_amount >= fine.final_amount:
            fine.status = FineStatusEnum.PAID
        elif fine.paid_amount > 0:
            fine.status = FineStatusEnum.PARTIAL

        # Update member outstanding fines
        member = await self.db.get(Member, fine.member_id)
        if member:
            member.outstanding_fines = max(Decimal("0"), member.outstanding_fines - data.amount)

        # Update transaction
        transaction = await self.db.get(IssueTransaction, fine.issue_id)
        if transaction:
            transaction.fine_paid = fine.paid_amount

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def get_payment(self, payment_id: int) -> Optional[FinePayment]:
        result = await self.db.execute(
            select(FinePayment).options(selectinload(FinePayment.fine)).where(FinePayment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_member_fines_summary(self, member_id: int) -> dict:
        result = await self.db.execute(
            select(
                func.count(Fine.id).label("total_fines"),
                func.sum(Fine.final_amount).label("total_amount"),
                func.sum(Fine.paid_amount).label("paid_amount"),
                func.sum(Fine.final_amount - Fine.paid_amount).label("outstanding"),
            ).where(Fine.member_id == member_id)
        )
        row = result.first()
        return {
            "total_fines": row.total_fines or 0,
            "total_amount": row.total_amount or Decimal("0"),
            "paid_amount": row.paid_amount or Decimal("0"),
            "outstanding": row.outstanding or Decimal("0"),
        }

    async def get_overdue_books_with_fines(self) -> List[dict]:
        today = date.today()
        result = await self.db.execute(
            select(IssueTransaction)
            .options(
                selectinload(IssueTransaction.member),
                selectinload(IssueTransaction.book),
            )
            .where(
                IssueTransaction.status.in_([IssueStatusEnum.ISSUED, IssueStatusEnum.OVERDUE]),
                IssueTransaction.due_date < today,
            )
        )
        transactions = result.scalars().all()

        overdue_list = []
        for txn in transactions:
            overdue_days = (today - txn.due_date).days
            settings = await self.get_settings()
            chargeable_days = max(0, overdue_days - settings.grace_period_days)
            estimated_fine = Decimal(str(chargeable_days)) * settings.default_fine_per_day

            overdue_list.append({
                "transaction_id": txn.transaction_id,
                "member_name": f"{txn.member.first_name} {txn.member.last_name}",
                "member_id": txn.member.member_id,
                "book_title": txn.book.title,
                "book_isbn": txn.book.isbn,
                "due_date": txn.due_date,
                "overdue_days": overdue_days,
                "estimated_fine": estimated_fine,
                "status": txn.status.value,
            })
        return overdue_list

    async def get_settings(self) -> LibrarySettings:
        result = await self.db.execute(select(LibrarySettings))
        settings = result.scalar_one_or_none()
        if not settings:
            settings = LibrarySettings()
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings
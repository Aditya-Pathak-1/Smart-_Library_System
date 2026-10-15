from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.book import Book, BookCopy
from app.models.member import Member, MembershipStatusEnum
from app.models.issue import IssueTransaction, IssueStatusEnum
from app.models.fine import Fine, FineStatusEnum
from app.models.settings import LibrarySettings
from app.schemas.issue import IssueTransactionCreate, IssueTransactionUpdate, IssueTransactionReturn
from app.services.member import MemberService
from app.services.fine import FineService


class IssueService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.member_service = MemberService(db)
        self.fine_service = FineService(db)

    def _generate_transaction_id(self) -> str:
        import random
        import string
        return "TXN" + "".join(random.choices(string.digits, k=10))

    async def get_settings(self) -> LibrarySettings:
        result = await self.db.execute(select(LibrarySettings))
        settings = result.scalar_one_or_none()
        if not settings:
            settings = LibrarySettings()
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings

    async def issue_book(self, data: IssueTransactionCreate, issued_by: int) -> IssueTransaction:
        # Validate member
        member = await self.member_service.get_member(data.member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        can_borrow, reason = await self.member_service.can_borrow(data.member_id)
        if not can_borrow:
            raise HTTPException(status_code=400, detail=reason)

        # Validate book
        book = await self.db.get(Book, data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        if not book.is_active:
            raise HTTPException(status_code=400, detail="Book is not active")
        if book.available_copies <= 0:
            raise HTTPException(status_code=400, detail="No available copies")

        # Get specific copy or find available one
        copy = None
        if data.copy_id:
            copy = await self.db.get(BookCopy, data.copy_id)
            if not copy or copy.book_id != data.book_id:
                raise HTTPException(status_code=400, detail="Invalid book copy")
            if not copy.is_available:
                raise HTTPException(status_code=400, detail="Selected copy is not available")
        else:
            result = await self.db.execute(
                select(BookCopy).where(BookCopy.book_id == data.book_id, BookCopy.is_available == True).limit(1)
            )
            copy = result.scalar_one_or_none()
            if not copy:
                result = await self.db.execute(
                    select(func.max(BookCopy.copy_number)).where(BookCopy.book_id == data.book_id)
                )
                copy_number = (result.scalar() or 0) + 1
                copy = BookCopy(book_id=book.id, copy_number=copy_number)
                self.db.add(copy)
                await self.db.flush()

        # Get settings for due date
        settings = await self.get_settings()
        issue_date = date.today()
        borrowing_days = data.borrow_days or settings.default_borrowing_days
        due_date = data.due_date or (issue_date + timedelta(days=borrowing_days))

        # Create transaction
        transaction = IssueTransaction(
            transaction_id=self._generate_transaction_id(),
            member_id=data.member_id,
            book_id=data.book_id,
            copy_id=copy.id,
            issue_date=issue_date,
            due_date=due_date,
            status=IssueStatusEnum.ISSUED,
            issued_by=issued_by,
            notes=data.notes,
        )
        self.db.add(transaction)

        # Update book and copy availability
        book.available_copies -= 1
        copy.is_available = False

        await self.db.commit()
        await self.db.refresh(transaction)
        return await self.get_transaction(transaction.id)

    async def return_book(self, transaction_id: str, data: IssueTransactionReturn, returned_by: int) -> IssueTransaction:
        result = await self.db.execute(
            select(IssueTransaction).where(IssueTransaction.transaction_id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if transaction.status == IssueStatusEnum.RETURNED:
            raise HTTPException(status_code=400, detail="Book already returned")

        # Validate copy if provided
        if data.copy_id:
            copy = await self.db.get(BookCopy, data.copy_id)
            if not copy or copy.id != transaction.copy_id:
                raise HTTPException(status_code=400, detail="Invalid book copy")

        return_date = date.today()
        transaction.return_date = return_date
        transaction.returned_by = returned_by
        transaction.notes = data.notes or transaction.notes

        # Calculate overdue
        overdue_days = max(0, (return_date - transaction.due_date).days)
        settings = await self.get_settings()
        if overdue_days > settings.grace_period_days:
            chargeable_days = overdue_days - settings.grace_period_days
            fine_amount = chargeable_days * settings.default_fine_per_day
            transaction.fine_amount = fine_amount
            transaction.status = IssueStatusEnum.OVERDUE if fine_amount > 0 else IssueStatusEnum.RETURNED
        else:
            transaction.status = IssueStatusEnum.RETURNED

        # Update book and copy
        book = await self.db.get(Book, transaction.book_id)
        copy = await self.db.get(BookCopy, transaction.copy_id)
        if book:
            book.available_copies += 1
        if copy:
            copy.is_available = True

        await self.db.commit()

        # Create fine record if overdue
        if overdue_days > settings.grace_period_days:
            await self.fine_service.create_fine_from_return(transaction, overdue_days, settings.default_fine_per_day)

        await self.db.refresh(transaction)
        return await self.get_transaction(transaction.id)

    async def get_transaction(self, transaction_id: int) -> Optional[IssueTransaction]:
        result = await self.db.execute(
            select(IssueTransaction)
            .options(
                selectinload(IssueTransaction.member),
                selectinload(IssueTransaction.book).selectinload(Book.author),
                selectinload(IssueTransaction.book).selectinload(Book.category),
                selectinload(IssueTransaction.copy),
                selectinload(IssueTransaction.fine),
            )
            .where(IssueTransaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_transactions(
        self,
        skip: int = 0,
        limit: int = 20,
        member_id: Optional[int] = None,
        book_id: Optional[int] = None,
        status: Optional[IssueStatusEnum] = None,
        search: Optional[str] = None,
    ) -> tuple[List[IssueTransaction], int]:
        query = select(IssueTransaction).options(
            selectinload(IssueTransaction.member),
            selectinload(IssueTransaction.book).selectinload(Book.author),
        )

        if member_id:
            query = query.where(IssueTransaction.member_id == member_id)
        if book_id:
            query = query.where(IssueTransaction.book_id == book_id)
        if status:
            query = query.where(IssueTransaction.status == status)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                IssueTransaction.transaction_id.ilike(search_term) |
                IssueTransaction.member.has(Member.first_name.ilike(search_term)) |
                IssueTransaction.member.has(Member.last_name.ilike(search_term)) |
                IssueTransaction.book.has(Book.title.ilike(search_term)) |
                IssueTransaction.book.has(Book.isbn.ilike(search_term))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        result = await self.db.execute(query.order_by(IssueTransaction.issue_date.desc()).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def renew_book(self, transaction_id: str, issued_by: int) -> IssueTransaction:
        transaction = await self.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if transaction.status != IssueStatusEnum.ISSUED:
            raise HTTPException(status_code=400, detail="Can only renew issued books")

        settings = await self.get_settings()
        if transaction.renewed_count >= settings.max_renewal_count:
            raise HTTPException(status_code=400, detail="Maximum renewal limit reached")

        # Extend due date
        transaction.due_date += timedelta(days=settings.default_borrowing_days)
        transaction.renewed_count += 1
        transaction.issued_by = issued_by

        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_transaction_by_id(self, transaction_id: str) -> Optional[IssueTransaction]:
        result = await self.db.execute(
            select(IssueTransaction).where(IssueTransaction.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_overdue_transactions(self) -> List[IssueTransaction]:
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
        return list(result.scalars().all())

    async def update_overdue_status(self) -> int:
        today = date.today()
        result = await self.db.execute(
            select(IssueTransaction).where(
                IssueTransaction.status == IssueStatusEnum.ISSUED,
                IssueTransaction.due_date < today,
            )
        )
        transactions = result.scalars().all()
        count = 0
        for txn in transactions:
            txn.status = IssueStatusEnum.OVERDUE
            count += 1
        await self.db.commit()
        return count
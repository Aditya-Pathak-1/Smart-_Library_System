from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.book import Book
from app.models.category import Category
from app.models.author import Author
from app.models.member import Member
from app.models.issue import IssueTransaction, IssueStatusEnum
from app.models.fine import Fine, FinePayment, FineStatusEnum
from app.models.settings import LibrarySettings
from app.schemas.report import (
    ReportFilter, DashboardStats, ChartDataPoint, IssueReturnChartData,
    CategoryChartData, RecentActivityItem, OverdueBookItem,
    BookInventoryReportItem, IssuedBooksReportItem, OverdueBooksReportItem,
    MemberActivityReportItem, FineCollectionReportItem, MostBorrowedBookItem
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self) -> DashboardStats:
        # Total books
        total_books_result = await self.db.execute(
            select(func.sum(Book.total_copies)).where(Book.is_active == True)
        )
        total_books = total_books_result.scalar() or 0

        # Available books
        available_books_result = await self.db.execute(
            select(func.sum(Book.available_copies)).where(Book.is_active == True)
        )
        available_books = available_books_result.scalar() or 0

        # Issued books
        issued_books_result = await self.db.execute(
            select(func.count(IssueTransaction.id)).where(IssueTransaction.status == IssueStatusEnum.ISSUED)
        )
        issued_books = issued_books_result.scalar() or 0

        # Total members
        total_members_result = await self.db.execute(select(func.count(Member.id)))
        total_members = total_members_result.scalar() or 0

        # Active members
        active_members_result = await self.db.execute(
            select(func.count(Member.id)).where(Member.status == "active")
        )
        active_members = active_members_result.scalar() or 0

        # Overdue books
        overdue_books_result = await self.db.execute(
            select(func.count(IssueTransaction.id)).where(IssueTransaction.status == IssueStatusEnum.OVERDUE)
        )
        overdue_books = overdue_books_result.scalar() or 0

        # Total outstanding fines
        outstanding_fines_result = await self.db.execute(
            select(func.sum(Fine.final_amount - Fine.paid_amount)).where(
                Fine.status.in_([FineStatusEnum.PENDING, FineStatusEnum.PARTIAL])
            )
        )
        outstanding_fines = outstanding_fines_result.scalar() or Decimal("0")

        # Total fines collected
        collected_fines_result = await self.db.execute(
            select(func.sum(FinePayment.amount))
        )
        collected_fines = collected_fines_result.scalar() or Decimal("0")

        return DashboardStats(
            total_books=total_books,
            available_books=available_books,
            issued_books=issued_books,
            total_members=total_members,
            active_members=active_members,
            overdue_books=overdue_books,
            total_outstanding_fines=outstanding_fines,
            total_fines_collected=collected_fines,
        )

    async def get_issue_return_chart(self, days: int = 30) -> IssueReturnChartData:
        start_date = date.today() - timedelta(days=days)
        labels = []
        issues = []
        returns = []

        for i in range(days):
            current_date = start_date + timedelta(days=i)
            labels.append(current_date.strftime("%d/%m"))

            # Issues on this date
            issue_result = await self.db.execute(
                select(func.count(IssueTransaction.id)).where(
                    func.date(IssueTransaction.issue_date) == current_date
                )
            )
            issues.append(issue_result.scalar() or 0)

            # Returns on this date
            return_result = await self.db.execute(
                select(func.count(IssueTransaction.id)).where(
                    func.date(IssueTransaction.return_date) == current_date
                )
            )
            returns.append(return_result.scalar() or 0)

        return IssueReturnChartData(labels=labels, issues=issues, returns=returns)

    async def get_category_chart(self) -> CategoryChartData:
        result = await self.db.execute(
            select(Category.name, func.count(Book.id))
            .join(Book, Book.category_id == Category.id)
            .where(Book.is_active == True, Category.is_active == True)
            .group_by(Category.name)
            .order_by(func.count(Book.id).desc())
            .limit(10)
        )
        rows = result.all()
        labels = [row[0] for row in rows]
        values = [row[1] for row in rows]
        return CategoryChartData(labels=labels, values=values)

    async def get_recent_activity(self, limit: int = 10) -> List[RecentActivityItem]:
        activities = []

        # Recent issues
        recent_issues = await self.db.execute(
            select(IssueTransaction)
            .options(selectinload(IssueTransaction.member), selectinload(IssueTransaction.book))
            .order_by(IssueTransaction.created_at.desc())
            .limit(limit)
        )
        for txn in recent_issues.scalars().all():
            activities.append(RecentActivityItem(
                id=txn.id,
                type="issue",
                description=f"{txn.member.first_name} {txn.member.last_name} borrowed '{txn.book.title}'",
                date=txn.created_at,
                user_name=txn.issued_by_user.full_name if txn.issued_by_user else None,
            ))

        # Recent returns
        recent_returns = await self.db.execute(
            select(IssueTransaction)
            .options(selectinload(IssueTransaction.member), selectinload(IssueTransaction.book))
            .where(IssueTransaction.return_date.isnot(None))
            .order_by(IssueTransaction.return_date.desc())
            .limit(limit)
        )
        for txn in recent_returns.scalars().all():
            activities.append(RecentActivityItem(
                id=txn.id,
                type="return",
                description=f"{txn.member.first_name} {txn.member.last_name} returned '{txn.book.title}'",
                date=txn.return_date,
                user_name=txn.returned_by_user.full_name if txn.returned_by_user else None,
            ))

        # Recent member registrations
        recent_members = await self.db.execute(
            select(Member).order_by(Member.created_at.desc()).limit(limit)
        )
        for member in recent_members.scalars().all():
            activities.append(RecentActivityItem(
                id=member.id,
                type="registration",
                description=f"New member registered: {member.first_name} {member.last_name} ({member.member_id})",
                date=member.created_at,
            ))

        # Recent fine payments
        recent_payments = await self.db.execute(
            select(FinePayment)
            .options(selectinload(FinePayment.fine).selectinload(Fine.member))
            .order_by(FinePayment.payment_date.desc())
            .limit(limit)
        )
        for payment in recent_payments.scalars().all():
            activities.append(RecentActivityItem(
                id=payment.id,
                type="payment",
                description=f"Fine payment of ₹{payment.amount} by {payment.fine.member.first_name} {payment.fine.member.last_name}",
                date=payment.payment_date,
            ))

        # Sort all activities by date
        activities.sort(key=lambda x: x.date, reverse=True)
        return activities[:limit]

    async def get_overdue_books(self, limit: int = 10) -> List[OverdueBookItem]:
        today = date.today()
        result = await self.db.execute(
            select(IssueTransaction)
            .options(selectinload(IssueTransaction.member), selectinload(IssueTransaction.book))
            .where(
                IssueTransaction.status.in_([IssueStatusEnum.ISSUED, IssueStatusEnum.OVERDUE]),
                IssueTransaction.due_date < today,
            )
            .order_by(IssueTransaction.due_date)
            .limit(limit)
        )
        transactions = result.scalars().all()

        overdue_list = []
        for txn in transactions:
            overdue_days = (today - txn.due_date).days
            settings = await self.get_settings()
            chargeable_days = max(0, overdue_days - settings.grace_period_days)
            estimated_fine = Decimal(str(chargeable_days)) * settings.default_fine_per_day

            overdue_list.append(OverdueBookItem(
                transaction_id=txn.transaction_id,
                member_name=f"{txn.member.first_name} {txn.member.last_name}",
                member_id=txn.member.member_id,
                book_title=txn.book.title,
                book_isbn=txn.book.isbn,
                due_date=txn.due_date,
                overdue_days=overdue_days,
                estimated_fine=estimated_fine,
            ))
        return overdue_list

    async def get_book_inventory_report(self, filters: ReportFilter) -> List[BookInventoryReportItem]:
        query = select(Book).options(
            selectinload(Book.author), selectinload(Book.category)
        ).where(Book.is_active == True)

        if filters.category_id:
            query = query.where(Book.category_id == filters.category_id)
        if filters.author_id:
            query = query.where(Book.author_id == filters.author_id)

        result = await self.db.execute(query)
        books = result.scalars().all()

        report = []
        for book in books:
            report.append(BookInventoryReportItem(
                book_id=book.id,
                title=book.title,
                isbn=book.isbn,
                author=book.author.name if book.author else "Unknown",
                category=book.category.name if book.category else "Unknown",
                total_copies=book.total_copies,
                available_copies=book.available_copies,
                issued_copies=book.total_copies - book.available_copies,
                shelf_location=book.shelf_location,
            ))
        return report

    async def get_issued_books_report(self, filters: ReportFilter) -> List[IssuedBooksReportItem]:
        query = select(IssueTransaction).options(
            selectinload(IssueTransaction.member), selectinload(IssueTransaction.book)
        ).where(IssueTransaction.status.in_([IssueStatusEnum.ISSUED, IssueStatusEnum.OVERDUE]))

        if filters.start_date:
            query = query.where(IssueTransaction.issue_date >= filters.start_date)
        if filters.end_date:
            query = query.where(IssueTransaction.issue_date <= filters.end_date)

        result = await self.db.execute(query)
        transactions = result.scalars().all()

        report = []
        for txn in transactions:
            overdue_days = 0
            if txn.due_date < date.today():
                overdue_days = (date.today() - txn.due_date).days

            report.append(IssuedBooksReportItem(
                transaction_id=txn.transaction_id,
                book_title=txn.book.title,
                book_isbn=txn.book.isbn,
                member_name=f"{txn.member.first_name} {txn.member.last_name}",
                member_id=txn.member.member_id,
                issue_date=txn.issue_date,
                due_date=txn.due_date,
                status=txn.status.value,
                overdue_days=overdue_days,
            ))
        return report

    async def get_overdue_books_report(self, filters: ReportFilter) -> List[OverdueBooksReportItem]:
        today = date.today()
        query = select(IssueTransaction).options(
            selectinload(IssueTransaction.member), selectinload(IssueTransaction.book)
        ).where(
            IssueTransaction.status.in_([IssueStatusEnum.ISSUED, IssueStatusEnum.OVERDUE]),
            IssueTransaction.due_date < today,
        )

        if filters.start_date:
            query = query.where(IssueTransaction.due_date >= filters.start_date)
        if filters.end_date:
            query = query.where(IssueTransaction.due_date <= filters.end_date)

        result = await self.db.execute(query)
        transactions = result.scalars().all()

        report = []
        settings = await self.get_settings()
        for txn in transactions:
            overdue_days = (today - txn.due_date).days
            chargeable_days = max(0, overdue_days - settings.grace_period_days)
            estimated_fine = Decimal(str(chargeable_days)) * settings.default_fine_per_day

            report.append(OverdueBooksReportItem(
                transaction_id=txn.transaction_id,
                book_title=txn.book.title,
                book_isbn=txn.book.isbn,
                member_name=f"{txn.member.first_name} {txn.member.last_name}",
                member_id=txn.member.member_id,
                issue_date=txn.issue_date,
                due_date=txn.due_date,
                overdue_days=overdue_days,
                estimated_fine=estimated_fine,
            ))
        return report

    async def get_member_activity_report(self, filters: ReportFilter) -> List[MemberActivityReportItem]:
        query = select(Member).options(selectinload(Member.user))

        if filters.status:
            query = query.where(Member.status == filters.status)

        result = await self.db.execute(query)
        members = result.scalars().all()

        report = []
        for member in members:
            # Total borrowed
            total_result = await self.db.execute(
                select(func.count(IssueTransaction.id)).where(IssueTransaction.member_id == member.id)
            )
            total_borrowed = total_result.scalar() or 0

            # Currently issued
            issued_result = await self.db.execute(
                select(func.count(IssueTransaction.id)).where(
                    IssueTransaction.member_id == member.id,
                    IssueTransaction.status == IssueStatusEnum.ISSUED
                )
            )
            currently_issued = issued_result.scalar() or 0

            # Overdue
            overdue_result = await self.db.execute(
                select(func.count(IssueTransaction.id)).where(
                    IssueTransaction.member_id == member.id,
                    IssueTransaction.status == IssueStatusEnum.OVERDUE
                )
            )
            overdue_count = overdue_result.scalar() or 0

            # Fines
            fines_result = await self.db.execute(
                select(
                    func.sum(Fine.final_amount),
                    func.sum(Fine.paid_amount),
                    func.sum(Fine.final_amount - Fine.paid_amount),
                ).where(Fine.member_id == member.id)
            )
            fines_row = fines_result.first()
            total_fines = fines_row[0] or Decimal("0")
            fines_paid = fines_row[1] or Decimal("0")
            outstanding_fines = fines_row[2] or Decimal("0")

            report.append(MemberActivityReportItem(
                member_id=member.member_id,
                member_name=f"{member.first_name} {member.last_name}",
                email=member.email,
                total_borrowed=total_borrowed,
                currently_issued=currently_issued,
                overdue_count=overdue_count,
                total_fines=total_fines,
                fines_paid=fines_paid,
                outstanding_fines=outstanding_fines,
            ))
        return report

    async def get_fine_collection_report(self, filters: ReportFilter) -> List[FineCollectionReportItem]:
        query = select(FinePayment).options(
            selectinload(FinePayment.fine).selectinload(Fine.member),
            selectinload(FinePayment.fine).selectinload(Fine.issue).selectinload(IssueTransaction.book),
            selectinload(FinePayment.received_by_user),
        )

        if filters.start_date:
            query = query.where(func.date(FinePayment.payment_date) >= filters.start_date)
        if filters.end_date:
            query = query.where(func.date(FinePayment.payment_date) <= filters.end_date)

        result = await self.db.execute(query.order_by(FinePayment.payment_date.desc()))
        payments = result.scalars().all()

        report = []
        for payment in payments:
            report.append(FineCollectionReportItem(
                payment_id=payment.payment_id,
                receipt_number=payment.receipt_number,
                member_name=f"{payment.fine.member.first_name} {payment.fine.member.last_name}",
                member_id=payment.fine.member.member_id,
                book_title=payment.fine.issue.book.title if payment.fine.issue and payment.fine.issue.book else "N/A",
                amount=payment.amount,
                payment_method=payment.payment_method,
                payment_date=payment.payment_date,
                received_by=payment.received_by_user.full_name if payment.received_by_user else "Unknown",
            ))
        return report

    async def get_most_borrowed_books(self, limit: int = 10) -> List[MostBorrowedBookItem]:
        result = await self.db.execute(
            select(Book, func.count(IssueTransaction.id).label("borrow_count"))
            .join(IssueTransaction, IssueTransaction.book_id == Book.id)
            .options(selectinload(Book.author), selectinload(Book.category))
            .where(Book.is_active == True)
            .group_by(Book.id)
            .order_by(func.count(IssueTransaction.id).desc())
            .limit(limit)
        )
        rows = result.all()

        report = []
        for book, count in rows:
            report.append(MostBorrowedBookItem(
                book_id=book.id,
                title=book.title,
                isbn=book.isbn,
                author=book.author.name if book.author else "Unknown",
                category=book.category.name if book.category else "Unknown",
                borrow_count=count,
            ))
        return report

    async def get_settings(self) -> LibrarySettings:
        result = await self.db.execute(select(LibrarySettings))
        settings = result.scalar_one_or_none()
        if not settings:
            settings = LibrarySettings()
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings
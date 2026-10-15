from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
import csv
import io

from app.api.deps import get_db, get_current_active_user, require_librarian_or_admin, require_any_role
from app.schemas.report import (
    ReportFilter, DashboardStats, IssueReturnChartData, CategoryChartData,
    RecentActivityItem, OverdueBookItem, BookInventoryReportItem,
    IssuedBooksReportItem, OverdueBooksReportItem, MemberActivityReportItem,
    FineCollectionReportItem, MostBorrowedBookItem
)
from app.services.report import ReportService

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = ReportService(db)
    return await service.get_dashboard_stats()


@router.get("/dashboard/charts/issue-return", response_model=IssueReturnChartData)
async def get_issue_return_chart(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = ReportService(db)
    return await service.get_issue_return_chart(days=days)


@router.get("/dashboard/charts/categories", response_model=CategoryChartData)
async def get_category_chart(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = ReportService(db)
    return await service.get_category_chart()


@router.get("/dashboard/recent-activity", response_model=list[RecentActivityItem])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = ReportService(db)
    return await service.get_recent_activity(limit=limit)


@router.get("/dashboard/overdue", response_model=list[OverdueBookItem])
async def get_overdue_books(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = ReportService(db)
    return await service.get_overdue_books(limit=limit)


@router.get("/reports/inventory", response_model=list[BookInventoryReportItem])
async def get_inventory_report(
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(category_id=category_id, author_id=author_id)
    service = ReportService(db)
    return await service.get_book_inventory_report(filters)


@router.get("/reports/issued", response_model=list[IssuedBooksReportItem])
async def get_issued_books_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    service = ReportService(db)
    return await service.get_issued_books_report(filters)


@router.get("/reports/overdue", response_model=list[OverdueBooksReportItem])
async def get_overdue_books_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    service = ReportService(db)
    return await service.get_overdue_books_report(filters)


@router.get("/reports/members", response_model=list[MemberActivityReportItem])
async def get_member_activity_report(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(status=status)
    service = ReportService(db)
    return await service.get_member_activity_report(filters)


@router.get("/reports/fines", response_model=list[FineCollectionReportItem])
async def get_fine_collection_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    service = ReportService(db)
    return await service.get_fine_collection_report(filters)


@router.get("/reports/most-borrowed", response_model=list[MostBorrowedBookItem])
async def get_most_borrowed_books(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = ReportService(db)
    return await service.get_most_borrowed_books(limit=limit)


# CSV Export endpoints
@router.get("/reports/inventory/export")
async def export_inventory_report(
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(category_id=category_id, author_id=author_id)
    service = ReportService(db)
    data = await service.get_book_inventory_report(filters)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Book ID", "Title", "ISBN", "Author", "Category", "Total Copies", "Available Copies", "Issued Copies", "Shelf Location"])
    for item in data:
        writer.writerow([item.book_id, item.title, item.isbn, item.author, item.category, item.total_copies, item.available_copies, item.issued_copies, item.shelf_location or ""])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_report.csv"}
    )


@router.get("/reports/issued/export")
async def export_issued_books_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    service = ReportService(db)
    data = await service.get_issued_books_report(filters)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Transaction ID", "Book Title", "ISBN", "Member Name", "Member ID", "Issue Date", "Due Date", "Status", "Overdue Days"])
    for item in data:
        writer.writerow([item.transaction_id, item.book_title, item.book_isbn, item.member_name, item.member_id, item.issue_date, item.due_date, item.status, item.overdue_days])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=issued_books_report.csv"}
    )


@router.get("/reports/overdue/export")
async def export_overdue_books_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    service = ReportService(db)
    data = await service.get_overdue_books_report(filters)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Transaction ID", "Book Title", "ISBN", "Member Name", "Member ID", "Issue Date", "Due Date", "Overdue Days", "Estimated Fine"])
    for item in data:
        writer.writerow([item.transaction_id, item.book_title, item.book_isbn, item.member_name, item.member_id, item.issue_date, item.due_date, item.overdue_days, item.estimated_fine])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=overdue_books_report.csv"}
    )


@router.get("/reports/fines/export")
async def export_fine_collection_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    service = ReportService(db)
    data = await service.get_fine_collection_report(filters)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Payment ID", "Receipt Number", "Member Name", "Member ID", "Book Title", "Amount", "Payment Method", "Payment Date", "Received By"])
    for item in data:
        writer.writerow([item.payment_id, item.receipt_number, item.member_name, item.member_id, item.book_title, item.amount, item.payment_method, item.payment_date, item.received_by])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fine_collection_report.csv"}
    )
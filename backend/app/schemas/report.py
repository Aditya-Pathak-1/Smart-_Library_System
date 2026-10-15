from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class ReportFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[int] = None
    author_id: Optional[int] = None
    member_id: Optional[int] = None
    status: Optional[str] = None


class DashboardStats(BaseModel):
    total_books: int
    available_books: int
    issued_books: int
    total_members: int
    active_members: int
    overdue_books: int
    total_outstanding_fines: Decimal
    total_fines_collected: Decimal


class ChartDataPoint(BaseModel):
    label: str
    value: int


class IssueReturnChartData(BaseModel):
    labels: List[str]
    issues: List[int]
    returns: List[int]


class CategoryChartData(BaseModel):
    labels: List[str]
    values: List[int]


class RecentActivityItem(BaseModel):
    id: int
    type: str
    description: str
    date: datetime
    user_name: Optional[str] = None


class OverdueBookItem(BaseModel):
    transaction_id: str
    member_name: str
    member_id: str
    book_title: str
    book_isbn: str
    due_date: date
    overdue_days: int
    estimated_fine: Decimal


class BookInventoryReportItem(BaseModel):
    book_id: int
    title: str
    isbn: str
    author: str
    category: str
    total_copies: int
    available_copies: int
    issued_copies: int
    shelf_location: Optional[str] = None


class IssuedBooksReportItem(BaseModel):
    transaction_id: str
    book_title: str
    book_isbn: str
    member_name: str
    member_id: str
    issue_date: date
    due_date: date
    status: str
    overdue_days: int


class OverdueBooksReportItem(BaseModel):
    transaction_id: str
    book_title: str
    book_isbn: str
    member_name: str
    member_id: str
    issue_date: date
    due_date: date
    overdue_days: int
    estimated_fine: Decimal


class MemberActivityReportItem(BaseModel):
    member_id: str
    member_name: str
    email: str
    total_borrowed: int
    currently_issued: int
    overdue_count: int
    total_fines: Decimal
    fines_paid: Decimal
    outstanding_fines: Decimal


class FineCollectionReportItem(BaseModel):
    payment_id: str
    receipt_number: str
    member_name: str
    member_id: str
    book_title: str
    amount: Decimal
    payment_method: str
    payment_date: datetime
    received_by: str


class MostBorrowedBookItem(BaseModel):
    book_id: int
    title: str
    isbn: str
    author: str
    category: str
    borrow_count: int


class ReportResponse(BaseModel):
    generated_at: datetime
    filters: ReportFilter
    data: List[dict]
    total_records: int
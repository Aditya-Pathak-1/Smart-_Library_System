from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

from app.schemas.member import MemberResponse
from app.schemas.book import BookResponse


class IssueTransactionBase(BaseModel):
    member_id: int
    book_id: int
    copy_id: Optional[int] = None
    due_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class IssueTransactionCreate(IssueTransactionBase):
    pass


class IssueTransactionUpdate(BaseModel):
    due_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    renewed_count: Optional[int] = Field(None, ge=0)


class IssueTransactionReturn(BaseModel):
    transaction_id: str
    copy_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)


class IssueTransactionResponse(IssueTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    issue_date: date
    return_date: Optional[date] = None
    status: str
    fine_amount: Decimal
    fine_paid: Decimal
    renewed_count: int
    issued_by: int
    returned_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    member: Optional[MemberResponse] = None
    book: Optional[BookResponse] = None


class IssueTransactionDetailResponse(IssueTransactionResponse):
    is_overdue: bool = False
    overdue_days: int = 0
    estimated_fine: Decimal = Decimal("0.00")
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

from app.schemas.member import MemberResponse


class FineBase(BaseModel):
    member_id: int
    issue_id: int
    overdue_days: int = Field(default=0, ge=0)
    fine_per_day: Decimal = Field(..., ge=0)
    calculated_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    waived_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    final_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class FineCreate(FineBase):
    pass


class FineUpdate(BaseModel):
    waived_amount: Optional[Decimal] = Field(None, ge=0)
    final_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(pending|partial|paid|waived)$")


class FinePaymentCreate(BaseModel):
    fine_id: int
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(default="cash", max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class FinePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: str
    fine_id: int
    amount: Decimal
    payment_method: str
    payment_date: datetime
    receipt_number: str
    received_by: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FineResponse(FineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fine_id: str
    paid_amount: Decimal
    status: str
    calculated_at: datetime
    finalized_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    member: Optional[MemberResponse] = None
    payments: List[FinePaymentResponse] = []


class FineDetailResponse(FineResponse):
    outstanding_balance: Decimal = Decimal("0.00")
    is_finalized: bool = False


class FineCalculationResponse(BaseModel):
    issue_id: int
    overdue_days: int
    fine_per_day: Decimal
    estimated_fine: Decimal
    grace_period_days: int = 0
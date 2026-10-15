from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from decimal import Decimal


class MemberBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[date] = None
    membership_type: str = Field(default="standard", max_length=50)
    registration_date: date
    expiry_date: Optional[date] = None
    max_books_allowed: int = Field(default=5, ge=1)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[date] = None
    membership_type: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended|expired)$")
    max_books_allowed: Optional[int] = Field(None, ge=1)


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: str
    status: str
    outstanding_fines: Decimal
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int] = None


class MemberDetailResponse(MemberResponse):
    currently_issued_books: int = 0
    total_books_borrowed: int = 0
    overdue_books: int = 0
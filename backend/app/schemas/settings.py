from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class LibrarySettingsBase(BaseModel):
    library_name: str = Field(default="Smart Library", max_length=255)
    library_address: Optional[str] = Field(None, max_length=500)
    library_phone: Optional[str] = Field(None, max_length=20)
    library_email: Optional[str] = Field(None, max_length=255)

    default_borrowing_days: int = Field(default=14, ge=1, le=365)
    default_fine_per_day: Decimal = Field(default=Decimal("5.00"), ge=0)
    max_books_per_member: int = Field(default=5, ge=1, le=50)
    max_renewal_count: int = Field(default=2, ge=0, le=10)
    grace_period_days: int = Field(default=0, ge=0, le=30)

    allow_online_registration: bool = True
    require_email_verification: bool = False
    send_due_reminders: bool = True
    reminder_days_before: int = Field(default=3, ge=1, le=30)

    currency_symbol: str = Field(default="₹", max_length=5)
    date_format: str = Field(default="DD/MM/YYYY", max_length=20)
    timezone: str = Field(default="Asia/Kolkata", max_length=50)


class LibrarySettingsUpdate(BaseModel):
    library_name: Optional[str] = Field(None, max_length=255)
    library_address: Optional[str] = Field(None, max_length=500)
    library_phone: Optional[str] = Field(None, max_length=20)
    library_email: Optional[str] = Field(None, max_length=255)
    default_borrowing_days: Optional[int] = Field(None, ge=1, le=365)
    default_fine_per_day: Optional[Decimal] = Field(None, ge=0)
    max_books_per_member: Optional[int] = Field(None, ge=1, le=50)
    max_renewal_count: Optional[int] = Field(None, ge=0, le=10)
    grace_period_days: Optional[int] = Field(None, ge=0, le=30)
    allow_online_registration: Optional[bool] = None
    require_email_verification: Optional[bool] = None
    send_due_reminders: Optional[bool] = None
    reminder_days_before: Optional[int] = Field(None, ge=1, le=30)
    currency_symbol: Optional[str] = Field(None, max_length=5)
    date_format: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)


class LibrarySettingsResponse(LibrarySettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
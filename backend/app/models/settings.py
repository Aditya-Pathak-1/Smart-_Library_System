from sqlalchemy import String, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class LibrarySettings(Base, TimestampMixin):
    __tablename__ = "library_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    library_name: Mapped[str] = mapped_column(String(255), default="Smart Library", nullable=False)
    library_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    library_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    library_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    default_borrowing_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    default_fine_per_day: Mapped[float] = mapped_column(Numeric(10, 2), default=5.00, nullable=False)
    max_books_per_member: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_renewal_count: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    grace_period_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    allow_online_registration: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    require_email_verification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    send_due_reminders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_days_before: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    currency_symbol: Mapped[str] = mapped_column(String(5), default="₹", nullable=False)
    date_format: Mapped[str] = mapped_column(String(20), default="DD/MM/YYYY", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = 1
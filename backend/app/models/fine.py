import enum
from datetime import datetime

from sqlalchemy import String, Date, DateTime, ForeignKey, Enum, Numeric, Index, CheckConstraint, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class FineStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    WAIVED = "waived"


class Fine(Base, TimestampMixin):
    __tablename__ = "fines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fine_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issue_transactions.id", ondelete="RESTRICT"), nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fine_per_day: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    calculated_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    waived_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    final_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    status: Mapped[FineStatusEnum] = mapped_column(
        Enum(FineStatusEnum), default=FineStatusEnum.PENDING, nullable=False, index=True
    )
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    member: Mapped["Member"] = relationship("Member", back_populates="fines", lazy="selectin")
    issue: Mapped["IssueTransaction"] = relationship("IssueTransaction", back_populates="fine", lazy="selectin")
    payments: Mapped[list["FinePayment"]] = relationship("FinePayment", back_populates="fine", lazy="selectin")

    __table_args__ = (
        CheckConstraint("overdue_days >= 0", name="ck_fines_overdue_days_nonnegative"),
        CheckConstraint("fine_per_day >= 0", name="ck_fines_per_day_nonnegative"),
        CheckConstraint("calculated_amount >= 0", name="ck_fines_calculated_nonnegative"),
        CheckConstraint("final_amount >= 0", name="ck_fines_final_nonnegative"),
        CheckConstraint("paid_amount >= 0", name="ck_fines_paid_nonnegative"),
        CheckConstraint("paid_amount <= final_amount", name="ck_fines_paid_lte_final"),
        CheckConstraint("waived_amount >= 0", name="ck_fines_waived_nonnegative"),
        Index("ix_fines_member_status", "member_id", "status"),
        Index("ix_fines_status_date", "status", "calculated_at"),
    )


class FinePayment(Base, TimestampMixin):
    __tablename__ = "fine_payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    payment_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    fine_id: Mapped[int] = mapped_column(ForeignKey("fines.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="cash", nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    receipt_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    received_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    fine: Mapped["Fine"] = relationship("Fine", back_populates="payments", lazy="selectin")
    received_by_user: Mapped["User"] = relationship("User", lazy="selectin")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
        Index("ix_payments_fine_date", "fine_id", "payment_date"),
        Index("ix_payments_receipt", "receipt_number"),
    )
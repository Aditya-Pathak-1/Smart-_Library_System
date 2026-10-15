import enum
from datetime import date

from sqlalchemy import String, Date, DateTime, ForeignKey, Enum, Numeric, Index, CheckConstraint, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class IssueStatusEnum(str, enum.Enum):
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"


class IssueTransaction(Base, TimestampMixin):
    __tablename__ = "issue_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="RESTRICT"), nullable=False)
    copy_id: Mapped[int | None] = mapped_column(ForeignKey("book_copies.id", ondelete="SET NULL"), nullable=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[IssueStatusEnum] = mapped_column(
        Enum(IssueStatusEnum), default=IssueStatusEnum.ISSUED, nullable=False, index=True
    )
    fine_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    fine_paid: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    renewed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    issued_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    returned_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    member: Mapped["Member"] = relationship("Member", back_populates="issues", lazy="selectin")
    book: Mapped["Book"] = relationship("Book", back_populates="issues", lazy="selectin")
    copy: Mapped["BookCopy"] = relationship("BookCopy", back_populates="issues", lazy="selectin")
    issued_by_user: Mapped["User"] = relationship("User", foreign_keys=[issued_by], lazy="selectin")
    returned_by_user: Mapped["User"] = relationship("User", foreign_keys=[returned_by], lazy="selectin")
    fine: Mapped["Fine"] = relationship("Fine", back_populates="issue", uselist=False, lazy="selectin")

    __table_args__ = (
        CheckConstraint("fine_amount >= 0", name="ck_issues_fine_nonnegative"),
        CheckConstraint("fine_paid >= 0", name="ck_issues_fine_paid_nonnegative"),
        CheckConstraint("fine_paid <= fine_amount", name="ck_issues_fine_paid_lte_amount"),
        CheckConstraint("renewed_count >= 0", name="ck_issues_renewed_nonnegative"),
        Index("ix_issues_member_status", "member_id", "status"),
        Index("ix_issues_book_status", "book_id", "status"),
        Index("ix_issues_due_date", "due_date"),
        Index("ix_issues_status_due", "status", "due_date"),
    )
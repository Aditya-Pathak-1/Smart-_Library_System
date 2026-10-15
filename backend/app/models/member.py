import enum
from datetime import date

from sqlalchemy import String, Date, ForeignKey, Enum, Numeric, Index, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class MembershipStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class Member(Base, TimestampMixin):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    member_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    membership_type: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    registration_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[MembershipStatusEnum] = mapped_column(
        Enum(MembershipStatusEnum), default=MembershipStatusEnum.ACTIVE, nullable=False, index=True
    )
    max_books_allowed: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    outstanding_fines: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="member_profile", lazy="selectin")
    issues: Mapped[list["IssueTransaction"]] = relationship("IssueTransaction", back_populates="member", lazy="selectin")
    fines: Mapped[list["Fine"]] = relationship("Fine", back_populates="member", lazy="selectin")

    __table_args__ = (
        CheckConstraint("outstanding_fines >= 0", name="ck_members_fines_nonnegative"),
        CheckConstraint("max_books_allowed > 0", name="ck_members_max_books_positive"),
        Index("ix_members_status_active", "status", "registration_date"),
        Index("ix_members_name", "first_name", "last_name"),
    )
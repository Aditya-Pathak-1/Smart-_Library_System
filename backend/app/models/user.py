import enum
from datetime import datetime

from sqlalchemy import String, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), default=RoleEnum.MEMBER, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(nullable=True)

    member_profile: Mapped["Member"] = relationship(
        "Member", back_populates="user", uselist=False, lazy="selectin"
    )

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )
from datetime import date

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Author(Base, TimestampMixin):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    biography: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author", lazy="selectin")

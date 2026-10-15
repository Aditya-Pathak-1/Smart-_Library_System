import enum
from sqlalchemy import String, Integer, ForeignKey, Enum, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shelf_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    available_copies: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    author: Mapped["Author"] = relationship("Author", back_populates="books", lazy="selectin")
    category: Mapped["Category"] = relationship("Category", back_populates="books", lazy="selectin")
    copies: Mapped[list["BookCopy"]] = relationship("BookCopy", back_populates="book", lazy="selectin")
    issues: Mapped[list["IssueTransaction"]] = relationship("IssueTransaction", back_populates="book", lazy="selectin")

    __table_args__ = (
        CheckConstraint("total_copies >= 0", name="ck_books_total_copies_nonnegative"),
        CheckConstraint("available_copies >= 0", name="ck_books_available_copies_nonnegative"),
        CheckConstraint("available_copies <= total_copies", name="ck_books_available_lte_total"),
        Index("ix_books_title_active", "title", "is_active"),
        Index("ix_books_author_category", "author_id", "category_id"),
    )


class BookCopy(Base, TimestampMixin):
    __tablename__ = "book_copies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    copy_number: Mapped[int] = mapped_column(Integer, nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    condition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    book: Mapped["Book"] = relationship("Book", back_populates="copies", lazy="selectin")
    issues: Mapped[list["IssueTransaction"]] = relationship("IssueTransaction", back_populates="copy", lazy="selectin")

    __table_args__ = (
        Index("ix_book_copies_book_available", "book_id", "is_available"),
    )
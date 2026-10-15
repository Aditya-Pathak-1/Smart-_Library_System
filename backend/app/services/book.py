from datetime import date
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.book import Book, BookCopy
from app.models.category import Category
from app.models.author import Author
from app.schemas.book import (
    BookCreate, BookUpdate, BookCopyCreate, BookCopyUpdate,
    CategoryCreate, CategoryUpdate, AuthorCreate, AuthorUpdate
)


class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Category methods
    async def create_category(self, data: CategoryCreate) -> Category:
        result = await self.db.execute(select(Category).where(Category.name == data.name))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Category already exists")
        category = Category(**data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_categories(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Category]:
        query = select(Category)
        if active_only:
            query = query.where(Category.is_active == True)
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Category.name))
        return list(result.scalars().all())

    async def get_category(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = await self.get_category(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, category_id: int) -> None:
        category = await self.get_category(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        await self.db.delete(category)
        await self.db.commit()

    # Author methods
    async def create_author(self, data: AuthorCreate) -> Author:
        author = Author(**data.model_dump())
        self.db.add(author)
        await self.db.commit()
        await self.db.refresh(author)
        return author

    async def get_authors(self, skip: int = 0, limit: int = 100) -> List[Author]:
        result = await self.db.execute(select(Author).offset(skip).limit(limit).order_by(Author.name))
        return list(result.scalars().all())

    async def get_author(self, author_id: int) -> Optional[Author]:
        result = await self.db.execute(select(Author).where(Author.id == author_id))
        return result.scalar_one_or_none()

    async def update_author(self, author_id: int, data: AuthorUpdate) -> Author:
        author = await self.get_author(author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(author, field, value)
        await self.db.commit()
        await self.db.refresh(author)
        return author

    async def delete_author(self, author_id: int) -> None:
        author = await self.get_author(author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        await self.db.delete(author)
        await self.db.commit()

    # Book methods
    async def create_book(self, data: BookCreate) -> Book:
        result = await self.db.execute(select(Book).where(Book.isbn == data.isbn))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Book with this ISBN already exists")

        book = Book(**data.model_dump(), available_copies=data.total_copies)
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)

        # Create book copies
        for i in range(1, data.total_copies + 1):
            copy = BookCopy(book_id=book.id, copy_number=i)
            self.db.add(copy)
        await self.db.commit()

        return await self.get_book(book.id)

    async def get_books(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        available_only: bool = False,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> tuple[List[Book], int]:
        query = select(Book).options(selectinload(Book.author), selectinload(Book.category)).where(Book.is_active == True)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Book.title.ilike(search_term),
                    Book.isbn.ilike(search_term),
                    Book.author.has(Author.name.ilike(search_term)),
                    Book.category.has(Category.name.ilike(search_term)),
                )
            )
        if category_id:
            query = query.where(Book.category_id == category_id)
        if author_id:
            query = query.where(Book.author_id == author_id)
        if available_only:
            query = query.where(Book.available_copies > 0)
        if year_from:
            query = query.where(Book.publication_year >= year_from)
        if year_to:
            query = query.where(Book.publication_year <= year_to)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Sorting
        sort_column = getattr(Book, sort_by, Book.title)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

        result = await self.db.execute(query.offset(skip).limit(limit))
        books = list(result.scalars().all())
        return books, total

    async def get_book(self, book_id: int) -> Optional[Book]:
        result = await self.db.execute(
            select(Book).options(selectinload(Book.author), selectinload(Book.category), selectinload(Book.copies))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def update_book(self, book_id: int, data: BookUpdate) -> Book:
        book = await self.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        update_data = data.model_dump(exclude_unset=True)

        # Handle total_copies change
        if "total_copies" in update_data:
            new_total = update_data["total_copies"]
            diff = new_total - book.total_copies
            if diff > 0:
                # Add new copies
                for i in range(book.total_copies + 1, new_total + 1):
                    copy = BookCopy(book_id=book.id, copy_number=i)
                    self.db.add(copy)
            elif diff < 0:
                # Remove available copies only
                available_to_remove = min(abs(diff), book.available_copies)
                result = await self.db.execute(
                    select(BookCopy)
                    .where(BookCopy.book_id == book_id, BookCopy.is_available == True)
                    .order_by(BookCopy.copy_number.desc())
                    .limit(available_to_remove)
                )
                copies_to_remove = result.scalars().all()
                for copy in copies_to_remove:
                    await self.db.delete(copy)
            book.available_copies += diff
            if book.available_copies < 0:
                book.available_copies = 0
            book.total_copies = new_total

        for field, value in update_data.items():
            if field != "total_copies":
                setattr(book, field, value)

        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete_book(self, book_id: int) -> None:
        book = await self.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        # Check if any copies are issued
        from app.models.issue import IssueTransaction, IssueStatusEnum
        result = await self.db.execute(
            select(IssueTransaction).where(
                IssueTransaction.book_id == book_id,
                IssueTransaction.status == IssueStatusEnum.ISSUED
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Cannot delete book with active issues")
        await self.db.delete(book)
        await self.db.commit()

    # Book Copy methods
    async def get_book_copies(self, book_id: int) -> List[BookCopy]:
        result = await self.db.execute(
            select(BookCopy).where(BookCopy.book_id == book_id).order_by(BookCopy.copy_number)
        )
        return list(result.scalars().all())

    async def create_book_copy(self, data: BookCopyCreate) -> BookCopy:
        book = await self.get_book(data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Get next copy number
        result = await self.db.execute(
            select(func.max(BookCopy.copy_number)).where(BookCopy.book_id == data.book_id)
        )
        max_copy = result.scalar() or 0
        copy_number = data.copy_number or max_copy + 1

        copy = BookCopy(book_id=data.book_id, copy_number=copy_number, barcode=data.barcode,
                        condition=data.condition, notes=data.notes)
        self.db.add(copy)
        book.total_copies += 1
        book.available_copies += 1
        await self.db.commit()
        await self.db.refresh(copy)
        return copy

    async def update_book_copy(self, copy_id: int, data: BookCopyUpdate) -> BookCopy:
        result = await self.db.execute(select(BookCopy).where(BookCopy.id == copy_id))
        copy = result.scalar_one_or_none()
        if not copy:
            raise HTTPException(status_code=404, detail="Book copy not found")

        update_data = data.model_dump(exclude_unset=True)
        if "is_available" in update_data:
            old_available = copy.is_available
            new_available = update_data["is_available"]
            if old_available != new_available:
                book = await self.get_book(copy.book_id)
                if book:
                    if new_available:
                        book.available_copies += 1
                    else:
                        book.available_copies = max(0, book.available_copies - 1)

        for field, value in update_data.items():
            setattr(copy, field, value)

        await self.db.commit()
        await self.db.refresh(copy)
        return copy

    async def delete_book_copy(self, copy_id: int) -> None:
        result = await self.db.execute(select(BookCopy).where(BookCopy.id == copy_id))
        copy = result.scalar_one_or_none()
        if not copy:
            raise HTTPException(status_code=404, detail="Book copy not found")

        # Check if copy is currently issued
        from app.models.issue import IssueTransaction, IssueStatusEnum
        issued = await self.db.execute(
            select(IssueTransaction).where(
                IssueTransaction.copy_id == copy_id,
                IssueTransaction.status == IssueStatusEnum.ISSUED
            )
        )
        if issued.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Cannot delete copy that is currently issued")

        book = await self.get_book(copy.book_id)
        if book:
            if copy.is_available:
                book.available_copies = max(0, book.available_copies - 1)
            book.total_copies = max(0, book.total_copies - 1)

        await self.db.delete(copy)
        await self.db.commit()
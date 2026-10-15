from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    require_librarian_or_admin,
    require_any_role,
)
from app.schemas.book import (
    BookCreate, BookUpdate, BookResponse,
    BookCopyCreate, BookCopyUpdate, BookCopyResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    AuthorCreate, AuthorUpdate, AuthorResponse,
)
from app.services.book import BookService

router = APIRouter()


# Category endpoints
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.create_category(data)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    return await service.get_categories(skip=skip, limit=limit, active_only=active_only)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.update_category(category_id, data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = BookService(db)
    await service.delete_category(category_id)


# Author endpoints
@router.post("/authors", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: AuthorCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.create_author(data)


@router.get("/authors", response_model=list[AuthorResponse])
async def list_authors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    return await service.get_authors(skip=skip, limit=limit)


@router.get("/authors/{author_id}", response_model=AuthorResponse)
async def get_author(
    author_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    author = await service.get_author(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.patch("/authors/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int,
    data: AuthorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.update_author(author_id, data)


@router.delete("/authors/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = BookService(db)
    await service.delete_author(author_id)


# Book endpoints
@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.create_book(data)


@router.get("", response_model=list[BookResponse])
async def list_books(
    response: Response,
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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    books, total = await service.get_books(
        skip=skip, limit=limit, search=search, category_id=category_id,
        author_id=author_id, available_only=available_only,
        year_from=year_from, year_to=year_to, sort_by=sort_by, sort_order=sort_order
    )
    response.headers["X-Total-Count"] = str(total)
    return books


@router.get("/stats")
async def get_books_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    from sqlalchemy import select, func
    from app.models.book import Book

    total = await db.scalar(select(func.count(Book.id)).where(Book.is_active == True)) or 0
    available = await db.scalar(select(func.sum(Book.available_copies)).where(Book.is_active == True)) or 0
    total_copies = await db.scalar(select(func.sum(Book.total_copies)).where(Book.is_active == True)) or 0

    return {
        "total_titles": total,
        "total_copies": total_copies,
        "available_copies": available,
        "issued_copies": total_copies - available,
    }


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.update_book(book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = BookService(db)
    await service.delete_book(book_id)


# Book Copy endpoints
@router.post("/{book_id}/copies", response_model=BookCopyResponse, status_code=status.HTTP_201_CREATED)
async def create_book_copy(
    book_id: int,
    data: BookCopyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    data.book_id = book_id
    return await service.create_book_copy(data)


@router.get("/{book_id}/copies", response_model=list[BookCopyResponse])
async def list_book_copies(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = BookService(db)
    return await service.get_book_copies(book_id)


@router.patch("/copies/{copy_id}", response_model=BookCopyResponse)
async def update_book_copy(
    copy_id: int,
    data: BookCopyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = BookService(db)
    return await service.update_book_copy(copy_id, data)


@router.delete("/copies/{copy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_copy(
    copy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = BookService(db)
    await service.delete_book_copy(copy_id)
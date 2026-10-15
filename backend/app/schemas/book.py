from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    books_count: int = 0


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    biography: Optional[str] = Field(None, max_length=2000)
    birth_date: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    biography: Optional[str] = Field(None, max_length=2000)
    birth_date: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)


class AuthorResponse(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    books_count: int = 0


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    isbn: str = Field(..., min_length=10, max_length=13)
    author_id: int
    category_id: int
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)
    shelf_location: Optional[str] = Field(None, max_length=100)
    total_copies: int = Field(default=1, ge=1)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)
    shelf_location: Optional[str] = Field(None, max_length=100)
    total_copies: Optional[int] = Field(None, ge=0)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_copies: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    author: Optional[AuthorResponse] = None
    category: Optional[CategoryResponse] = None


class BookCopyBase(BaseModel):
    book_id: int
    copy_number: int = Field(..., ge=1)
    barcode: Optional[str] = Field(None, max_length=50)
    condition: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class BookCopyCreate(BookCopyBase):
    pass


class BookCopyUpdate(BaseModel):
    copy_number: Optional[int] = Field(None, ge=1)
    barcode: Optional[str] = Field(None, max_length=50)
    is_available: Optional[bool] = None
    condition: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class BookCopyResponse(BookCopyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.user import User, RoleEnum
from app.models.category import Category
from app.models.author import Author
from app.models.book import Book, BookCopy
from app.models.member import Member, MembershipStatusEnum
from app.models.settings import LibrarySettings

settings = get_settings()

TEST_DATABASE_URL = settings.DATABASE_URL_TEST or "postgresql+asyncpg://postgres:postgres@localhost:5432/smart_library_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database):
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(setup_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Test Admin",
        role=RoleEnum.ADMIN,
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def librarian_user(db_session: AsyncSession):
    user = User(
        email="librarian@test.com",
        hashed_password=get_password_hash("librarian123"),
        full_name="Test Librarian",
        role=RoleEnum.LIBRARIAN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def member_user(db_session: AsyncSession):
    user = User(
        email="member@test.com",
        hashed_password=get_password_hash("member123"),
        full_name="Test Member",
        role=RoleEnum.MEMBER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user: User):
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    return response.json()["access_token"]


@pytest.fixture
async def librarian_token(client: AsyncClient, librarian_user: User):
    response = await client.post("/api/v1/auth/login", json={
        "email": "librarian@test.com",
        "password": "librarian123"
    })
    return response.json()["access_token"]


@pytest.fixture
async def member_token(client: AsyncClient, member_user: User):
    response = await client.post("/api/v1/auth/login", json={
        "email": "member@test.com",
        "password": "member123"
    })
    return response.json()["access_token"]


@pytest.fixture
async def test_category(db_session: AsyncSession):
    category = Category(name="Test Category", description="Test Description")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_author(db_session: AsyncSession):
    author = Author(name="Test Author", biography="Test Biography")
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)
    return author


@pytest.fixture
async def test_book(db_session: AsyncSession, test_category: Category, test_author: Author):
    book = Book(
        title="Test Book",
        isbn="9780000000001",
        author_id=test_author.id,
        category_id=test_category.id,
        total_copies=5,
        available_copies=5,
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book


@pytest.fixture
async def test_book_copies(db_session: AsyncSession, test_book: Book):
    copies = [
        BookCopy(book_id=test_book.id, copy_number=copy_number)
        for copy_number in range(1, test_book.total_copies + 1)
    ]
    db_session.add_all(copies)
    await db_session.commit()
    return copies


@pytest.fixture
async def test_member(db_session: AsyncSession, member_user: User):
    from datetime import date, timedelta
    member = Member(
        user_id=member_user.id,
        member_id="MEMTEST001",
        first_name="Test",
        last_name="Member",
        email="member@test.com",
        registration_date=date.today(),
        expiry_date=date.today() + timedelta(days=365),
        status=MembershipStatusEnum.ACTIVE,
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(member)
    return member
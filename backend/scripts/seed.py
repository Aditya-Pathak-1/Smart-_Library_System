import asyncio
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.user import User, RoleEnum
from app.models.category import Category
from app.models.author import Author
from app.models.book import Book, BookCopy
from app.models.member import Member, MembershipStatusEnum
from app.models.settings import LibrarySettings
from app.core.security import get_password_hash


async def seed_database():
    async with async_session_maker() as db:
        # Check if already seeded
        result = await db.execute(select(User).where(User.email == "admin@library.com"))
        if result.scalar_one_or_none():
            print("Database already seeded!")
            return

        print("Seeding database...")

        # Create admin user
        admin = User(
            email="admin@library.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=RoleEnum.ADMIN,
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)

        # Create librarian user
        librarian = User(
            email="librarian@library.com",
            hashed_password=get_password_hash("librarian123"),
            full_name="Head Librarian",
            role=RoleEnum.LIBRARIAN,
            is_active=True,
        )
        db.add(librarian)

        # Create member users
        member1_user = User(
            email="john.doe@email.com",
            hashed_password=get_password_hash("member123"),
            full_name="John Doe",
            role=RoleEnum.MEMBER,
            is_active=True,
        )
        db.add(member1_user)

        member2_user = User(
            email="jane.smith@email.com",
            hashed_password=get_password_hash("member123"),
            full_name="Jane Smith",
            role=RoleEnum.MEMBER,
            is_active=True,
        )
        db.add(member2_user)

        await db.flush()

        # Create categories
        categories = [
            Category(name="Fiction", description="Fiction books including novels, short stories"),
            Category(name="Non-Fiction", description="Non-fiction books including biographies, history"),
            Category(name="Science & Technology", description="Science, technology, engineering books"),
            Category(name="Computer Science", description="Programming, algorithms, software development"),
            Category(name="Mathematics", description="Mathematics, statistics, applied math"),
            Category(name="Literature", description="Classic and contemporary literature"),
            Category(name="Business & Economics", description="Business, economics, finance books"),
            Category(name="Self Help", description="Personal development, psychology, self-help"),
        ]
        for cat in categories:
            db.add(cat)
        await db.flush()

        # Create authors
        authors = [
            Author(name="George Orwell", biography="English novelist and essayist", birth_date=date(1903, 6, 25), nationality="British"),
            Author(name="Jane Austen", biography="English novelist", birth_date=date(1775, 12, 16), nationality="British"),
            Author(name="Isaac Asimov", biography="American author and professor of biochemistry", birth_date=date(1920, 1, 2), nationality="American"),
            Author(name="Robert C. Martin", biography="Software engineer and author", birth_date=date(1952, 12, 5), nationality="American"),
            Author(name="Martin Fowler", biography="Software developer and author", birth_date=date(1963, 1, 1), nationality="British"),
            Author(name="Thomas H. Cormen", biography="Computer science professor", birth_date=date(1956, 1, 1), nationality="American"),
            Author(name="Stephen Hawking", biography="Theoretical physicist", birth_date=date(1942, 1, 8), nationality="British"),
            Author(name="Daniel Kahneman", biography="Nobel Prize winning psychologist", birth_date=date(1934, 3, 5), nationality="Israeli-American"),
        ]
        for auth in authors:
            db.add(auth)
        await db.flush()

        # Create books
        books_data = [
            {
                "title": "1984",
                "isbn": "9780451524935",
                "author_id": 1,
                "category_id": 1,
                "publisher": "Signet Classic",
                "publication_year": 1950,
                "shelf_location": "A1-FIC-001",
                "total_copies": 5,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg",
                "description": "Dystopian novel about totalitarian surveillance state",
            },
            {
                "title": "Animal Farm",
                "isbn": "9780451526342",
                "author_id": 1,
                "category_id": 1,
                "publisher": "Signet Classic",
                "publication_year": 1945,
                "shelf_location": "A1-FIC-002",
                "total_copies": 3,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780451526342-L.jpg",
                "description": "Allegorical novella about farm animals rebellion",
            },
            {
                "title": "Pride and Prejudice",
                "isbn": "9780141439518",
                "author_id": 2,
                "category_id": 6,
                "publisher": "Penguin Classics",
                "publication_year": 1813,
                "shelf_location": "A2-LIT-001",
                "total_copies": 4,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg",
                "description": "Classic romantic novel of manners",
            },
            {
                "title": "Foundation",
                "isbn": "9780553293357",
                "author_id": 3,
                "category_id": 1,
                "publisher": "Spectra",
                "publication_year": 1951,
                "shelf_location": "A1-FIC-003",
                "total_copies": 3,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780553293357-L.jpg",
                "description": "First book in the Foundation series",
            },
            {
                "title": "Clean Code",
                "isbn": "9780132350884",
                "author_id": 4,
                "category_id": 4,
                "publisher": "Prentice Hall",
                "publication_year": 2008,
                "shelf_location": "B1-CS-001",
                "total_copies": 5,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780132350884-L.jpg",
                "description": "Handbook of agile software craftsmanship",
            },
            {
                "title": "Refactoring",
                "isbn": "9780201485677",
                "author_id": 5,
                "category_id": 4,
                "publisher": "Addison-Wesley",
                "publication_year": 1999,
                "shelf_location": "B1-CS-002",
                "total_copies": 3,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780201485677-L.jpg",
                "description": "Improving the design of existing code",
            },
            {
                "title": "Introduction to Algorithms",
                "isbn": "9780262033848",
                "author_id": 6,
                "category_id": 4,
                "publisher": "MIT Press",
                "publication_year": 2009,
                "shelf_location": "B1-CS-003",
                "total_copies": 2,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780262033848-L.jpg",
                "description": "Comprehensive algorithms textbook",
            },
            {
                "title": "A Brief History of Time",
                "isbn": "9780553380163",
                "author_id": 7,
                "category_id": 3,
                "publisher": "Bantam Books",
                "publication_year": 1988,
                "shelf_location": "A3-SCI-001",
                "total_copies": 4,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg",
                "description": "From Big Bang to black holes",
            },
            {
                "title": "Thinking, Fast and Slow",
                "isbn": "9780374533557",
                "author_id": 8,
                "category_id": 8,
                "publisher": "Farrar, Straus and Giroux",
                "publication_year": 2011,
                "shelf_location": "A4-SELF-001",
                "total_copies": 3,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg",
                "description": "Nobel laureate's work on decision making",
            },
            {
                "title": "The Great Gatsby",
                "isbn": "9780743273565",
                "author_id": 2,
                "category_id": 6,
                "publisher": "Scribner",
                "publication_year": 1925,
                "shelf_location": "A2-LIT-002",
                "total_copies": 4,
                "cover_image_url": "https://covers.openlibrary.org/b/isbn/9780743273565-L.jpg",
                "description": "Classic American novel of the Jazz Age",
            },
        ]

        books = []
        for book_data in books_data:
            book = Book(**book_data, available_copies=book_data["total_copies"])
            db.add(book)
            books.append(book)
        await db.flush()

        for book in books:
            for copy_number in range(1, book.total_copies + 1):
                db.add(BookCopy(book_id=book.id, copy_number=copy_number))

        # Create members
        members = [
            Member(
                user_id=member1_user.id,
                member_id="MEM00000001",
                first_name="John",
                last_name="Doe",
                email="john.doe@email.com",
                phone="+91-9876543210",
                address="123 Main Street, Mumbai, Maharashtra 400001",
                date_of_birth=date(1990, 5, 15),
                membership_type="premium",
                registration_date=date.today() - timedelta(days=365),
                expiry_date=date.today() + timedelta(days=365),
                status=MembershipStatusEnum.ACTIVE,
                max_books_allowed=10,
            ),
            Member(
                user_id=member2_user.id,
                member_id="MEM00000002",
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@email.com",
                phone="+91-9876543211",
                address="456 Park Avenue, Delhi, Delhi 110001",
                date_of_birth=date(1995, 8, 22),
                membership_type="standard",
                registration_date=date.today() - timedelta(days=180),
                expiry_date=date.today() + timedelta(days=180),
                status=MembershipStatusEnum.ACTIVE,
                max_books_allowed=5,
            ),
            Member(
                member_id="MEM00000003",
                first_name="Robert",
                last_name="Johnson",
                email="robert.johnson@email.com",
                phone="+91-9876543212",
                address="789 Oak Road, Bangalore, Karnataka 560001",
                date_of_birth=date(1988, 12, 3),
                membership_type="student",
                registration_date=date.today() - timedelta(days=90),
                expiry_date=date.today() + timedelta(days=275),
                status=MembershipStatusEnum.ACTIVE,
                max_books_allowed=3,
            ),
            Member(
                member_id="MEM00000004",
                first_name="Emily",
                last_name="Williams",
                email="emily.williams@email.com",
                phone="+91-9876543213",
                address="321 Pine Lane, Chennai, Tamil Nadu 600001",
                date_of_birth=date(1992, 3, 18),
                membership_type="standard",
                registration_date=date.today() - timedelta(days=30),
                expiry_date=date.today() + timedelta(days=335),
                status=MembershipStatusEnum.ACTIVE,
                max_books_allowed=5,
            ),
        ]
        for member in members:
            db.add(member)
        await db.flush()

        # Create library settings
        settings = LibrarySettings(
            library_name="Smart Library System",
            library_address="123 Library Street, Knowledge City, India",
            library_phone="+91-22-12345678",
            library_email="info@smartlibrary.com",
        )
        db.add(settings)

        await db.commit()
        print("Database seeded successfully!")
        print("\nLogin credentials:")
        print("  Admin: admin@library.com / admin123")
        print("  Librarian: librarian@library.com / librarian123")
        print("  Member: john.doe@email.com / member123")
        print("  Member: jane.smith@email.com / member123")


if __name__ == "__main__":
    asyncio.run(seed_database())
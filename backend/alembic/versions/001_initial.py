"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("admin", "librarian", "member", name="roleenum"), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email_active", "users", ["email", "is_active"])

    # Create categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_categories_name_active", "categories", ["name", "is_active"])

    # Create authors table
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("biography", sa.String(2000), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_authors_name", "authors", ["name"])

    # Create books table
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("isbn", sa.String(13), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("publisher", sa.String(255), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("shelf_location", sa.String(100), nullable=True),
        sa.Column("total_copies", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("available_copies", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("cover_image_url", sa.String(500), nullable=True),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("isbn"),
        sa.CheckConstraint("total_copies >= 0", name="ck_books_total_copies_nonnegative"),
        sa.CheckConstraint("available_copies >= 0", name="ck_books_available_copies_nonnegative"),
        sa.CheckConstraint("available_copies <= total_copies", name="ck_books_available_lte_total"),
    )
    op.create_index("ix_books_title_active", "books", ["title", "is_active"])
    op.create_index("ix_books_author_category", "books", ["author_id", "category_id"])

    # Create book_copies table
    op.create_table(
        "book_copies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("copy_number", sa.Integer(), nullable=False),
        sa.Column("barcode", sa.String(50), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("condition", sa.String(100), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barcode"),
    )
    op.create_index("ix_book_copies_book_available", "book_copies", ["book_id", "is_available"])
    op.create_index("ix_book_copies_barcode", "book_copies", ["barcode"])

    # Create members table
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("member_id", sa.String(20), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("membership_type", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("registration_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Enum("active", "inactive", "suspended", "expired", name="membershipstatusenum"), nullable=False, server_default="active"),
        sa.Column("max_books_allowed", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("outstanding_fines", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id"),
        sa.UniqueConstraint("email"),
        sa.CheckConstraint("outstanding_fines >= 0", name="ck_members_fines_nonnegative"),
        sa.CheckConstraint("max_books_allowed > 0", name="ck_members_max_books_positive"),
    )
    op.create_index("ix_members_status_active", "members", ["status", "registration_date"])
    op.create_index("ix_members_name", "members", ["first_name", "last_name"])

    # Create issue_transactions table
    op.create_table(
        "issue_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.String(30), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("copy_id", sa.Integer(), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Enum("issued", "returned", "overdue", "lost", name="issuestatusenum"), nullable=False, server_default="issued"),
        sa.Column("fine_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("fine_paid", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("renewed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("issued_by", sa.Integer(), nullable=False),
        sa.Column("returned_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["copy_id"], ["book_copies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["issued_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["returned_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
        sa.CheckConstraint("fine_amount >= 0", name="ck_issues_fine_nonnegative"),
        sa.CheckConstraint("fine_paid >= 0", name="ck_issues_fine_paid_nonnegative"),
        sa.CheckConstraint("fine_paid <= fine_amount", name="ck_issues_fine_paid_lte_amount"),
        sa.CheckConstraint("renewed_count >= 0", name="ck_issues_renewed_nonnegative"),
    )
    op.create_index("ix_issues_member_status", "issue_transactions", ["member_id", "status"])
    op.create_index("ix_issues_book_status", "issue_transactions", ["book_id", "status"])
    op.create_index("ix_issues_due_date", "issue_transactions", ["due_date"])
    op.create_index("ix_issues_status_due", "issue_transactions", ["status", "due_date"])

    # Create fines table
    op.create_table(
        "fines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fine_id", sa.String(30), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column("overdue_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fine_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("calculated_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("waived_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("final_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("paid_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("status", sa.Enum("pending", "partial", "paid", "waived", name="finestatusenum"), nullable=False, server_default="pending"),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issue_transactions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fine_id"),
        sa.CheckConstraint("overdue_days >= 0", name="ck_fines_overdue_days_nonnegative"),
        sa.CheckConstraint("fine_per_day >= 0", name="ck_fines_per_day_nonnegative"),
        sa.CheckConstraint("calculated_amount >= 0", name="ck_fines_calculated_nonnegative"),
        sa.CheckConstraint("final_amount >= 0", name="ck_fines_final_nonnegative"),
        sa.CheckConstraint("paid_amount >= 0", name="ck_fines_paid_nonnegative"),
        sa.CheckConstraint("paid_amount <= final_amount", name="ck_fines_paid_lte_final"),
        sa.CheckConstraint("waived_amount >= 0", name="ck_fines_waived_nonnegative"),
    )
    op.create_index("ix_fines_member_status", "fines", ["member_id", "status"])
    op.create_index("ix_fines_status_date", "fines", ["status", "calculated_at"])

    # Create fine_payments table
    op.create_table(
        "fine_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.String(30), nullable=False),
        sa.Column("fine_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="cash"),
        sa.Column("payment_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("receipt_number", sa.String(30), nullable=False),
        sa.Column("received_by", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["fine_id"], ["fines.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["received_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_id"),
        sa.UniqueConstraint("receipt_number"),
        sa.CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )
    op.create_index("ix_payments_fine_date", "fine_payments", ["fine_id", "payment_date"])
    op.create_index("ix_payments_receipt", "fine_payments", ["receipt_number"])

    # Create library_settings table
    op.create_table(
        "library_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("library_name", sa.String(255), nullable=False, server_default="Smart Library"),
        sa.Column("library_address", sa.String(500), nullable=True),
        sa.Column("library_phone", sa.String(20), nullable=True),
        sa.Column("library_email", sa.String(255), nullable=True),
        sa.Column("default_borrowing_days", sa.Integer(), nullable=False, server_default="14"),
        sa.Column("default_fine_per_day", sa.Numeric(10, 2), nullable=False, server_default="5.00"),
        sa.Column("max_books_per_member", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("max_renewal_count", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("allow_online_registration", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("require_email_verification", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("send_due_reminders", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("reminder_days_before", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("currency_symbol", sa.String(5), nullable=False, server_default="₹"),
        sa.Column("date_format", sa.String(20), nullable=False, server_default="DD/MM/YYYY"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("library_settings")
    op.drop_table("fine_payments")
    op.drop_table("fines")
    op.drop_table("issue_transactions")
    op.drop_table("members")
    op.drop_table("book_copies")
    op.drop_table("books")
    op.drop_table("authors")
    op.drop_table("categories")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS roleenum")
    op.execute("DROP TYPE IF EXISTS membershipstatusenum")
    op.execute("DROP TYPE IF EXISTS issuestatusenum")
    op.execute("DROP TYPE IF EXISTS finestatusenum")
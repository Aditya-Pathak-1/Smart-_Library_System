from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.member import Member, MembershipStatusEnum
from app.models.user import User
from app.schemas.member import MemberCreate, MemberUpdate


class MemberService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_member_id(self) -> str:
        import random
        import string
        return "MEM" + "".join(random.choices(string.digits, k=8))

    async def create_member(self, data: MemberCreate) -> Member:
        result = await self.db.execute(select(Member).where(Member.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Member with this email already exists")

        member_id = self._generate_member_id()
        while True:
            result = await self.db.execute(select(Member).where(Member.member_id == member_id))
            if not result.scalar_one_or_none():
                break
            member_id = self._generate_member_id()

        member = Member(**data.model_dump(), member_id=member_id)
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def get_members(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[MembershipStatusEnum] = None,
    ) -> tuple[List[Member], int]:
        query = select(Member)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Member.first_name.ilike(search_term),
                    Member.last_name.ilike(search_term),
                    Member.email.ilike(search_term),
                    Member.member_id.ilike(search_term),
                    Member.phone.ilike(search_term),
                )
            )
        if status:
            query = query.where(Member.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        result = await self.db.execute(query.order_by(Member.created_at.desc()).offset(skip).limit(limit))
        members = list(result.scalars().all())
        return members, total

    async def get_member(self, member_id: int) -> Optional[Member]:
        result = await self.db.execute(select(Member).where(Member.id == member_id))
        return result.scalar_one_or_none()

    async def get_member_by_user(self, user_id: int) -> Optional[Member]:
        result = await self.db.execute(select(Member).where(Member.user_id == user_id))
        return result.scalar_one_or_none()

    async def update_member(self, member_id: int, data: MemberUpdate) -> Member:
        member = await self.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data:
            update_data["status"] = MembershipStatusEnum(update_data["status"])
        if "email" in update_data:
            result = await self.db.execute(
                select(Member).where(Member.email == update_data["email"], Member.id != member_id)
            )
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already in use")

        for field, value in update_data.items():
            setattr(member, field, value)

        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def delete_member(self, member_id: int) -> None:
        member = await self.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Check if member has active issues
        from app.models.issue import IssueTransaction, IssueStatusEnum
        result = await self.db.execute(
            select(IssueTransaction).where(
                IssueTransaction.member_id == member_id,
                IssueTransaction.status == IssueStatusEnum.ISSUED
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Cannot delete member with active issues")

        await self.db.delete(member)
        await self.db.commit()

    async def get_member_detail(self, member_id: int) -> dict:
        member = await self.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Get currently issued books count
        from app.models.issue import IssueTransaction, IssueStatusEnum
        issued_result = await self.db.execute(
            select(func.count(IssueTransaction.id)).where(
                IssueTransaction.member_id == member_id,
                IssueTransaction.status == IssueStatusEnum.ISSUED
            )
        )
        currently_issued = issued_result.scalar() or 0

        # Get total borrowed count
        total_result = await self.db.execute(
            select(func.count(IssueTransaction.id)).where(
                IssueTransaction.member_id == member_id
            )
        )
        total_borrowed = total_result.scalar() or 0

        # Get overdue count
        overdue_result = await self.db.execute(
            select(func.count(IssueTransaction.id)).where(
                IssueTransaction.member_id == member_id,
                IssueTransaction.status == IssueStatusEnum.OVERDUE
            )
        )
        overdue_count = overdue_result.scalar() or 0

        return {
            **member.__dict__,
            "currently_issued_books": currently_issued,
            "total_books_borrowed": total_borrowed,
            "overdue_books": overdue_count,
        }

    async def get_member_history(self, member_id: int, skip: int = 0, limit: int = 20) -> List:
        from app.models.issue import IssueTransaction
        result = await self.db.execute(
            select(IssueTransaction)
            .options(selectinload(IssueTransaction.book), selectinload(IssueTransaction.fine))
            .where(IssueTransaction.member_id == member_id)
            .order_by(IssueTransaction.issue_date.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def can_borrow(self, member_id: int) -> tuple[bool, str]:
        member = await self.get_member(member_id)
        if not member:
            return False, "Member not found"
        if member.status != MembershipStatusEnum.ACTIVE:
            return False, f"Member status is {member.status.value}"

        from app.models.issue import IssueTransaction, IssueStatusEnum
        result = await self.db.execute(
            select(func.count(IssueTransaction.id)).where(
                IssueTransaction.member_id == member_id,
                IssueTransaction.status == IssueStatusEnum.ISSUED
            )
        )
        current_issued = result.scalar() or 0

        if current_issued >= member.max_books_allowed:
            return False, f"Member has reached maximum borrowing limit ({member.max_books_allowed})"

        if member.outstanding_fines > 0:
            return False, f"Member has outstanding fines of ₹{member.outstanding_fines}"

        return True, "OK"
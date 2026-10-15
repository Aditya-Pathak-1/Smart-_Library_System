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
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse, MemberDetailResponse
from app.services.member import MemberService

router = APIRouter()


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    data: MemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = MemberService(db)
    return await service.create_member(data)


@router.get("", response_model=list[MemberResponse])
async def list_members(
    response: Response,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    from app.models.member import MembershipStatusEnum
    service = MemberService(db)
    status_enum = MembershipStatusEnum(status) if status else None
    members, total = await service.get_members(skip=skip, limit=limit, search=search, status=status_enum)
    response.headers["X-Total-Count"] = str(total)
    return members


@router.get("/stats")
async def get_members_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    from sqlalchemy import select, func
    from app.models.member import Member, MembershipStatusEnum

    total = await db.scalar(select(func.count(Member.id))) or 0
    active = await db.scalar(select(func.count(Member.id)).where(Member.status == MembershipStatusEnum.ACTIVE)) or 0
    inactive = await db.scalar(select(func.count(Member.id)).where(Member.status == MembershipStatusEnum.INACTIVE)) or 0
    suspended = await db.scalar(select(func.count(Member.id)).where(Member.status == MembershipStatusEnum.SUSPENDED)) or 0

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "suspended": suspended,
    }


@router.get("/{member_id}", response_model=MemberDetailResponse)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = MemberService(db)
    detail = await service.get_member_detail(member_id)
    return detail


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: int,
    data: MemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = MemberService(db)
    return await service.update_member(member_id, data)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = MemberService(db)
    await service.delete_member(member_id)


@router.get("/{member_id}/history")
async def get_member_history(
    member_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = MemberService(db)
    history = await service.get_member_history(member_id, skip=skip, limit=limit)
    return history


@router.get("/profile", response_model=MemberDetailResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    service = MemberService(db)
    member = await service.get_member_by_user(current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    return await service.get_member_detail(member.id)


@router.get("/profile/history")
async def get_my_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    service = MemberService(db)
    member = await service.get_member_by_user(current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    return await service.get_member_history(member.id, skip=skip, limit=limit)
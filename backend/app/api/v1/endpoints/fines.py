from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_active_user, require_librarian_or_admin, require_any_role
from app.schemas.fine import (
    FineUpdate, FinePaymentCreate, FinePaymentResponse,
    FineResponse, FineDetailResponse, FineCalculationResponse
)
from app.services.fine import FineService

router = APIRouter()


@router.get("/fines", response_model=list[FineResponse])
async def list_fines(
    response: Response,
    skip: int = 0,
    limit: int = 20,
    member_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    from app.models.fine import FineStatusEnum
    service = FineService(db)
    status_enum = FineStatusEnum(status) if status else None
    fines, total = await service.get_fines(skip=skip, limit=limit, member_id=member_id, status=status_enum, search=search)
    response.headers["X-Total-Count"] = str(total)
    return fines


@router.get("/fines/stats")
async def get_fines_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    from sqlalchemy import select, func
    from app.models.fine import Fine, FineStatusEnum, FinePayment

    total_fines = await db.scalar(select(func.count(Fine.id))) or 0
    pending = await db.scalar(select(func.count(Fine.id)).where(Fine.status == FineStatusEnum.PENDING)) or 0
    partial = await db.scalar(select(func.count(Fine.id)).where(Fine.status == FineStatusEnum.PARTIAL)) or 0
    paid = await db.scalar(select(func.count(Fine.id)).where(Fine.status == FineStatusEnum.PAID)) or 0
    waived = await db.scalar(select(func.count(Fine.id)).where(Fine.status == FineStatusEnum.WAIVED)) or 0

    total_amount = await db.scalar(select(func.sum(Fine.final_amount))) or 0
    paid_amount = await db.scalar(select(func.sum(Fine.paid_amount))) or 0
    outstanding = await db.scalar(select(func.sum(Fine.final_amount - Fine.paid_amount)).where(
        Fine.status.in_([FineStatusEnum.PENDING, FineStatusEnum.PARTIAL])
    )) or 0

    collected = await db.scalar(select(func.sum(FinePayment.amount))) or 0

    return {
        "total_fines": total_fines,
        "pending": pending,
        "partial": partial,
        "paid": paid,
        "waived": waived,
        "total_amount": float(total_amount),
        "paid_amount": float(paid_amount),
        "outstanding": float(outstanding),
        "collected": float(collected),
    }


@router.get("/fines/overdue", response_model=list[FineCalculationResponse])
async def get_overdue_books_with_fines(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = FineService(db)
    return await service.get_overdue_books_with_fines()


@router.get("/fines/{fine_id}", response_model=FineDetailResponse)
async def get_fine(
    fine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = FineService(db)
    fine = await service.get_fine(fine_id)
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")

    outstanding = fine.final_amount - fine.paid_amount
    response = FineDetailResponse.model_validate(fine)
    response.outstanding_balance = outstanding
    response.is_finalized = fine.finalized_at is not None
    return response


@router.patch("/fines/{fine_id}", response_model=FineResponse)
async def update_fine(
    fine_id: int,
    data: FineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = FineService(db)
    return await service.update_fine(fine_id, data)


@router.post("/fines/pay", response_model=FinePaymentResponse, status_code=status.HTTP_201_CREATED)
async def record_payment(
    data: FinePaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = FineService(db)
    return await service.record_payment(data, current_user.id)


@router.get("/fines/payments/{payment_id}", response_model=FinePaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = FineService(db)
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/members/{member_id}/fines/summary")
async def get_member_fines_summary(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = FineService(db)
    return await service.get_member_fines_summary(member_id)
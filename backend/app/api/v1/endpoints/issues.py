from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_active_user, require_librarian_or_admin, require_any_role
from app.schemas.issue import (
    IssueTransactionCreate, IssueTransactionUpdate, IssueTransactionReturn,
    IssueTransactionResponse, IssueTransactionDetailResponse
)
from app.models.issue import IssueStatusEnum
from app.services.issue import IssueService

router = APIRouter()


@router.post("/issue", response_model=IssueTransactionResponse, status_code=status.HTTP_201_CREATED)
async def issue_book(
    data: IssueTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = IssueService(db)
    return await service.issue_book(data, current_user.id)


@router.post("/return", response_model=IssueTransactionResponse)
async def return_book(
    data: IssueTransactionReturn,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = IssueService(db)
    return await service.return_book(data.transaction_id, data, current_user.id)


@router.post("/renew/{transaction_id}", response_model=IssueTransactionResponse)
async def renew_book(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = IssueService(db)
    return await service.renew_book(transaction_id, current_user.id)


@router.get("/transactions", response_model=list[IssueTransactionResponse])
async def list_transactions(
    response: Response,
    skip: int = 0,
    limit: int = 20,
    member_id: Optional[int] = None,
    book_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    from app.models.issue import IssueStatusEnum
    service = IssueService(db)
    status_enum = IssueStatusEnum(status) if status else None
    transactions, total = await service.get_transactions(
        skip=skip, limit=limit, member_id=member_id, book_id=book_id,
        status=status_enum, search=search
    )
    response.headers["X-Total-Count"] = str(total)
    return transactions


@router.get("/transactions/stats")
async def get_transactions_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    from sqlalchemy import select, func
    from app.models.issue import IssueTransaction, IssueStatusEnum

    total = await db.scalar(select(func.count(IssueTransaction.id))) or 0
    issued = await db.scalar(select(func.count(IssueTransaction.id)).where(IssueTransaction.status == IssueStatusEnum.ISSUED)) or 0
    returned = await db.scalar(select(func.count(IssueTransaction.id)).where(IssueTransaction.status == IssueStatusEnum.RETURNED)) or 0
    overdue = await db.scalar(select(func.count(IssueTransaction.id)).where(IssueTransaction.status == IssueStatusEnum.OVERDUE)) or 0

    return {
        "total": total,
        "issued": issued,
        "returned": returned,
        "overdue": overdue,
    }


@router.get("/transactions/{transaction_id}", response_model=IssueTransactionDetailResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = IssueService(db)
    transaction = await service.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Calculate overdue info
    from datetime import date
    today = date.today()
    is_overdue = transaction.status == IssueStatusEnum.OVERDUE or (transaction.status == IssueStatusEnum.ISSUED and transaction.due_date < today)
    overdue_days = 0
    estimated_fine = 0

    if is_overdue:
        overdue_days = (today - transaction.due_date).days
        settings = await service.get_settings()
        chargeable_days = max(0, overdue_days - settings.grace_period_days)
        estimated_fine = chargeable_days * settings.default_fine_per_day

    # Build response
    response = IssueTransactionDetailResponse.model_validate(transaction)
    response.is_overdue = is_overdue
    response.overdue_days = overdue_days
    response.estimated_fine = estimated_fine
    return response


@router.get("/member/{member_id}/transactions", response_model=list[IssueTransactionResponse])
async def get_member_transactions(
    member_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = IssueService(db)
    transactions, _ = await service.get_transactions(skip=skip, limit=limit, member_id=member_id)
    return transactions


@router.post("/update-overdue-status")
async def update_overdue_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_librarian_or_admin),
):
    service = IssueService(db)
    count = await service.update_overdue_status()
    return {"updated": count}
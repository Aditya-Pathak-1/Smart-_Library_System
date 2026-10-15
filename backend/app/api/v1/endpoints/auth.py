from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user, require_admin
from app.schemas.auth import (
    UserCreate, UserUpdate, UserResponse, LoginRequest,
    RefreshTokenRequest, Token, MessageResponse
)
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.register(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.login(credentials)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.refresh_token(request.refresh_token)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user),
):
    return current_user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    role: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    from app.models.user import RoleEnum
    service = AuthService(db)
    role_enum = RoleEnum(role) if role else None
    users = await service.get_users(skip=skip, limit=limit, role=role_enum)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = AuthService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/impersonate/{user_id}", response_model=Token)
async def impersonate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = AuthService(db)
    return await service.impersonate_user(user_id, current_user.id)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = AuthService(db)
    user = await service.update_user(user_id, user_data)
    return user


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = AuthService(db)
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
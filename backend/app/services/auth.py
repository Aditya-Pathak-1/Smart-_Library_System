from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from jose import JWTError

from app.models.user import User, RoleEnum
from app.schemas.auth import UserCreate, UserUpdate, LoginRequest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_token_pair,
    decode_token,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate) -> User:
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=RoleEnum(user_data.role),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, credentials: LoginRequest) -> dict:
        result = await self.db.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        user.last_login = datetime.utcnow()
        await self.db.commit()
        return create_token_pair(user.id, user.email, user.role.value)

    async def refresh_token(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
            user_id = int(payload.get("sub"))
        except (JWTError, TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        impersonator_id = payload.get("impersonator_sub")
        if impersonator_id is not None:
            try:
                impersonator_id = int(impersonator_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=401, detail="Invalid impersonation token")

            administrator = await self.get_user(impersonator_id)
            if (
                not administrator
                or not administrator.is_active
                or administrator.role != RoleEnum.ADMIN
                or user.role == RoleEnum.ADMIN
            ):
                raise HTTPException(status_code=401, detail="Impersonation session is no longer valid")

            return create_token_pair(
                user.id,
                user.email,
                user.role.value,
                impersonator_id=administrator.id,
                refresh_expires_delta=timedelta(hours=1),
            )

        return create_token_pair(user.id, user.email, user.role.value)

    async def impersonate_user(self, user_id: int, administrator_id: int) -> dict:
        target = await self.get_user(user_id)
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if not target.is_active:
            raise HTTPException(status_code=400, detail="Cannot impersonate an inactive user")
        if target.role == RoleEnum.ADMIN:
            raise HTTPException(
                status_code=400,
                detail="Only librarian and member accounts can be impersonated",
            )

        return create_token_pair(
            target.id,
            target.email,
            target.role.value,
            impersonator_id=administrator_id,
            refresh_expires_delta=timedelta(hours=1),
        )

    async def get_user(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_users(
        self, skip: int = 0, limit: int = 20, role: Optional[RoleEnum] = None
    ) -> list[User]:
        query = select(User).offset(skip).limit(limit)
        if role:
            query = query.where(User.role == role)
        result = await self.db.execute(query.order_by(User.created_at.desc()))
        return list(result.scalars().all())

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        if "role" in update_data:
            update_data["role"] = RoleEnum(update_data["role"])

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await self.db.delete(user)
        await self.db.commit()
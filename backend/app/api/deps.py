from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, RoleEnum

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    impersonator_id = payload.get("impersonator_sub")
    if impersonator_id is not None:
        try:
            impersonator_id = int(impersonator_id)
        except (TypeError, ValueError):
            raise credentials_exception

        result = await db.execute(select(User).where(User.id == impersonator_id))
        administrator = result.scalar_one_or_none()
        if (
            not administrator
            or not administrator.is_active
            or administrator.role != RoleEnum.ADMIN
            or user.role == RoleEnum.ADMIN
        ):
            raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


def require_roles(*allowed_roles: RoleEnum):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
    return role_checker


require_admin = require_roles(RoleEnum.ADMIN)
require_librarian_or_admin = require_roles(RoleEnum.LIBRARIAN, RoleEnum.ADMIN)
require_any_role = require_roles(RoleEnum.ADMIN, RoleEnum.LIBRARIAN, RoleEnum.MEMBER)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user, require_admin, require_any_role
from app.schemas.settings import LibrarySettingsResponse, LibrarySettingsUpdate
from app.services.settings import SettingsService

router = APIRouter()


@router.get("/settings", response_model=LibrarySettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_any_role),
):
    service = SettingsService(db)
    return await service.get_settings()


@router.patch("/settings", response_model=LibrarySettingsResponse)
async def update_settings(
    data: LibrarySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
):
    service = SettingsService(db)
    return await service.update_settings(data)

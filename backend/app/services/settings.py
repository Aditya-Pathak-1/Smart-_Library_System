from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from decimal import Decimal

from app.models.settings import LibrarySettings
from app.schemas.settings import LibrarySettingsUpdate


class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_settings(self) -> LibrarySettings:
        result = await self.db.execute(select(LibrarySettings))
        settings = result.scalar_one_or_none()
        if not settings:
            settings = LibrarySettings()
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings

    async def update_settings(self, data: LibrarySettingsUpdate) -> LibrarySettings:
        settings = await self.get_settings()

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        await self.db.commit()
        await self.db.refresh(settings)
        return settings
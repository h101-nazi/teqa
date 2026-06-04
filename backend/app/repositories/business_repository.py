import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business


class BusinessRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, business_id: uuid.UUID) -> Business | None:
        result = await self.db.execute(select(Business).where(Business.id == business_id))
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: uuid.UUID) -> list[Business]:
        result = await self.db.execute(select(Business).where(Business.owner_id == owner_id))
        return list(result.scalars().all())

    async def create(self, business: Business) -> Business:
        self.db.add(business)
        await self.db.flush()
        await self.db.refresh(business)
        return business

    async def update(self, business: Business) -> Business:
        await self.db.flush()
        await self.db.refresh(business)
        return business

    async def get_all_active(self) -> list[Business]:
        result = await self.db.execute(
            select(Business).where(Business.is_onboarded.is_(True))
        )
        return list(result.scalars().all())

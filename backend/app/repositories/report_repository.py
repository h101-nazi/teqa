import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportDelivery


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def get_by_business(
        self, business_id: uuid.UUID, limit: int = 30
    ) -> list[Report]:
        result = await self.db.execute(
            select(Report)
            .where(Report.business_id == business_id)
            .order_by(Report.report_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_business_and_date(
        self, business_id: uuid.UUID, report_date: date
    ) -> Report | None:
        result = await self.db.execute(
            select(Report).where(
                Report.business_id == business_id,
                Report.report_date == report_date,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, report: Report) -> Report:
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def update(self, report: Report) -> Report:
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def create_delivery(self, delivery: ReportDelivery) -> ReportDelivery:
        self.db.add(delivery)
        await self.db.flush()
        await self.db.refresh(delivery)
        return delivery

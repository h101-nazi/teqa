import uuid
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportStatus
from app.repositories.report_repository import ReportRepository
from app.repositories.transaction_repository import TransactionRepository


class ReportService:
    def __init__(self, db: AsyncSession):
        self.report_repo = ReportRepository(db)
        self.txn_repo = TransactionRepository(db)

    async def generate_daily_report(self, business_id: uuid.UUID, report_date: date) -> Report:
        existing = await self.report_repo.get_by_business_and_date(business_id, report_date)
        if existing and existing.status == ReportStatus.GENERATED:
            return existing

        revenue = await self.txn_repo.get_daily_revenue(business_id, report_date)
        orders_count = await self.txn_repo.get_daily_orders_count(business_id, report_date)
        avg_order_value = revenue / orders_count if orders_count > 0 else 0.0

        # Calculate growth
        prev_date = report_date - timedelta(days=1)
        prev_revenue = await self.txn_repo.get_daily_revenue(business_id, prev_date)
        growth_pct = None
        if prev_revenue > 0:
            growth_pct = ((revenue - prev_revenue) / prev_revenue) * 100

        # Top products
        top_products = await self.txn_repo.get_top_products(business_id, report_date)
        top_product_name = top_products[0]["name"] if top_products else None

        metrics = {
            "revenue": revenue,
            "orders_count": orders_count,
            "avg_order_value": avg_order_value,
            "revenue_growth_pct": growth_pct,
            "top_products": top_products,
        }

        if existing:
            existing.revenue = revenue
            existing.orders_count = orders_count
            existing.avg_order_value = avg_order_value
            existing.revenue_growth_pct = growth_pct
            existing.top_product = top_product_name
            existing.metrics_json = metrics
            existing.status = ReportStatus.GENERATED
            return await self.report_repo.update(existing)

        report = Report(
            business_id=business_id,
            report_date=report_date,
            status=ReportStatus.GENERATED,
            revenue=revenue,
            orders_count=orders_count,
            avg_order_value=avg_order_value,
            revenue_growth_pct=growth_pct,
            top_product=top_product_name,
            metrics_json=metrics,
        )
        return await self.report_repo.create(report)

    async def get_reports(self, business_id: uuid.UUID, limit: int = 30) -> list[Report]:
        return await self.report_repo.get_by_business(business_id, limit)

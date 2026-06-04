import uuid
from datetime import date, datetime, time, timezone

from sqlalchemy import Float, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionItem


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_revenue(self, business_id: uuid.UUID, day: date) -> float:
        start = datetime.combine(day, time.min, tzinfo=timezone.utc)
        end = datetime.combine(day, time.max, tzinfo=timezone.utc)
        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.business_id == business_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                Transaction.status == "completed",
            )
        )
        return float(result.scalar_one())

    async def get_daily_orders_count(self, business_id: uuid.UUID, day: date) -> int:
        start = datetime.combine(day, time.min, tzinfo=timezone.utc)
        end = datetime.combine(day, time.max, tzinfo=timezone.utc)
        result = await self.db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.business_id == business_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                Transaction.status == "completed",
            )
        )
        return int(result.scalar_one())

    async def get_top_products(
        self, business_id: uuid.UUID, day: date, limit: int = 5
    ) -> list[dict]:
        start = datetime.combine(day, time.min, tzinfo=timezone.utc)
        end = datetime.combine(day, time.max, tzinfo=timezone.utc)
        result = await self.db.execute(
            select(
                TransactionItem.product_name,
                func.sum(TransactionItem.total_price).label("total_revenue"),
                func.sum(TransactionItem.quantity).label("total_quantity"),
            )
            .join(Transaction, TransactionItem.transaction_id == Transaction.id)
            .where(
                Transaction.business_id == business_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                Transaction.status == "completed",
            )
            .group_by(TransactionItem.product_name)
            .order_by(func.sum(TransactionItem.total_price).desc())
            .limit(limit)
        )
        rows = result.all()
        return [
            {"name": r[0], "revenue": float(r[1]), "quantity": int(r[2])}
            for r in rows
        ]

    async def bulk_create(self, transactions: list[Transaction]) -> None:
        self.db.add_all(transactions)
        await self.db.flush()

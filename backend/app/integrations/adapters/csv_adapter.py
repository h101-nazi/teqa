import io
import uuid
from datetime import date, timezone

import pandas as pd

from app.integrations.base import BaseIntegrationAdapter
from app.models.transaction import Transaction, TransactionItem


class CSVAdapter(BaseIntegrationAdapter):
    """Adapter for CSV file uploads."""

    def __init__(self):
        self.data: pd.DataFrame | None = None

    async def connect(self, credentials: dict) -> bool:
        return True

    async def test_connection(self) -> bool:
        return True

    async def sync_transactions(
        self, business_id: str, start_date: date, end_date: date
    ) -> list[Transaction]:
        if self.data is None:
            return []
        return self._parse_transactions(business_id)

    async def sync_products(self, business_id: str) -> list[dict]:
        return []

    async def sync_customers(self, business_id: str) -> list[dict]:
        return []

    def load_csv(self, file_content: bytes) -> pd.DataFrame:
        self.data = pd.read_csv(io.BytesIO(file_content))
        return self.data

    def _parse_transactions(self, business_id: str) -> list[Transaction]:
        if self.data is None:
            return []

        transactions = []
        required_cols = {"amount", "date"}
        if not required_cols.issubset(set(self.data.columns)):
            return []

        for _, row in self.data.iterrows():
            try:
                txn_date = pd.to_datetime(row["date"])
                txn = Transaction(
                    business_id=uuid.UUID(business_id),
                    amount=float(row["amount"]),
                    transaction_date=txn_date.to_pydatetime().replace(tzinfo=timezone.utc),
                    status="completed",
                    payment_method=row.get("payment_method", "unknown"),
                    items_count=int(row.get("items_count", 1)),
                )

                if "product_name" in row and pd.notna(row["product_name"]):
                    item = TransactionItem(
                        product_name=str(row["product_name"]),
                        quantity=int(row.get("quantity", 1)),
                        unit_price=float(row.get("unit_price", row["amount"])),
                        total_price=float(row["amount"]),
                    )
                    txn.items.append(item)

                transactions.append(txn)
            except (ValueError, KeyError):
                continue

        return transactions

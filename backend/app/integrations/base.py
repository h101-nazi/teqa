from abc import ABC, abstractmethod
from datetime import date

from app.models.transaction import Transaction


class BaseIntegrationAdapter(ABC):
    """Base class for all integration adapters."""

    @abstractmethod
    async def connect(self, credentials: dict) -> bool:
        """Validate credentials and establish connection."""
        ...

    @abstractmethod
    async def sync_transactions(
        self, business_id: str, start_date: date, end_date: date
    ) -> list[Transaction]:
        """Fetch transactions from the external source."""
        ...

    @abstractmethod
    async def sync_products(self, business_id: str) -> list[dict]:
        """Fetch products/inventory from the external source."""
        ...

    @abstractmethod
    async def sync_customers(self, business_id: str) -> list[dict]:
        """Fetch customers from the external source."""
        ...

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the connection is still valid."""
        ...

from datetime import date

import httpx

from app.integrations.base import BaseIntegrationAdapter
from app.models.transaction import Transaction


class PaymobAdapter(BaseIntegrationAdapter):
    BASE_URL = "https://accept.paymob.com/api"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.auth_token: str = ""

    async def connect(self, credentials: dict) -> bool:
        self.api_key = credentials.get("api_key", "")
        return await self.test_connection()

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/auth/tokens",
                    json={"api_key": self.api_key},
                    timeout=10.0,
                )
                if response.status_code == 201:
                    self.auth_token = response.json().get("token", "")
                    return True
        except Exception:
            pass
        return False

    async def _authenticate(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/tokens",
                json={"api_key": self.api_key},
                timeout=10.0,
            )
            if response.status_code == 201:
                self.auth_token = response.json().get("token", "")
        return self.auth_token

    async def sync_transactions(
        self, business_id: str, start_date: date, end_date: date
    ) -> list[Transaction]:
        if not self.auth_token:
            await self._authenticate()
        transactions = []
        try:
            async with httpx.AsyncClient() as client:
                page = 1
                while True:
                    response = await client.get(
                        f"{self.BASE_URL}/acceptance/transactions",
                        headers={"Authorization": f"Bearer {self.auth_token}"},
                        params={"page": page},
                        timeout=30.0,
                    )
                    if response.status_code != 200:
                        break
                    data = response.json()
                    results = data.get("results", [])
                    if not results:
                        break
                    transactions.extend(results)
                    if not data.get("next"):
                        break
                    page += 1
        except Exception:
            pass
        return transactions  # type: ignore

    async def sync_products(self, business_id: str) -> list[dict]:
        return []

    async def sync_customers(self, business_id: str) -> list[dict]:
        return []

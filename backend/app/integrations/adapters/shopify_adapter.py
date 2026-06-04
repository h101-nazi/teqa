from datetime import date

import httpx

from app.integrations.base import BaseIntegrationAdapter
from app.models.transaction import Transaction


class ShopifyAdapter(BaseIntegrationAdapter):
    def __init__(self, shop_url: str = "", access_token: str = ""):
        self.shop_url = shop_url
        self.access_token = access_token
        self.base_url = f"https://{shop_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }

    async def connect(self, credentials: dict) -> bool:
        self.shop_url = credentials.get("shop_url", "")
        self.access_token = credentials.get("access_token", "")
        self.base_url = f"https://{self.shop_url}/admin/api/2024-01"
        self.headers["X-Shopify-Access-Token"] = self.access_token
        return await self.test_connection()

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/shop.json",
                    headers=self.headers,
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def sync_transactions(
        self, business_id: str, start_date: date, end_date: date
    ) -> list[Transaction]:
        orders = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders.json",
                    headers=self.headers,
                    params={
                        "created_at_min": start_date.isoformat(),
                        "created_at_max": end_date.isoformat(),
                        "status": "any",
                        "limit": 250,
                    },
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    orders = data.get("orders", [])
        except Exception:
            pass
        return orders  # type: ignore

    async def sync_products(self, business_id: str) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products.json",
                    headers=self.headers,
                    params={"limit": 250},
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json().get("products", [])
        except Exception:
            pass
        return []

    async def sync_customers(self, business_id: str) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers.json",
                    headers=self.headers,
                    params={"limit": 250},
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json().get("customers", [])
        except Exception:
            pass
        return []

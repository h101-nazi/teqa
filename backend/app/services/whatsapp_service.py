import structlog
from httpx import AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = structlog.get_logger()


class WhatsAppService:
    def __init__(self):
        self.api_url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_message(self, to_number: str, message: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message},
        }

        async with AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            logger.info("WhatsApp message sent", to=to_number, message_id=data.get("messages", [{}])[0].get("id"))
            return data

    def format_daily_report(
        self,
        owner_name: str,
        currency: str,
        revenue: float,
        orders_count: int,
        orders_growth_pct: float | None,
        avg_order_value: float,
        top_product: str | None,
        inventory_alert: str | None,
        ai_insight: str,
        recommendation: str,
    ) -> str:
        growth_str = ""
        if orders_growth_pct is not None:
            sign = "+" if orders_growth_pct >= 0 else ""
            growth_str = f" ({sign}{orders_growth_pct:.0f}%)"

        lines = [
            f"Good Morning {owner_name} ☀️",
            "",
            "Yesterday Revenue:",
            f"{currency} {revenue:,.0f}",
            "",
            "Orders:",
            f"{orders_count}{growth_str}",
            "",
            "Average Order Value:",
            f"{currency} {avg_order_value:,.0f}",
        ]

        if top_product:
            lines.extend(["", "Top Product:", top_product])

        if inventory_alert:
            lines.extend(["", "Inventory Alert:", inventory_alert])

        lines.extend([
            "",
            "AI Insight:",
            ai_insight,
            "",
            "Recommendation:",
            recommendation,
            "",
            "Have a great day.",
            "",
            "— Teqa",
        ])

        return "\n".join(lines)

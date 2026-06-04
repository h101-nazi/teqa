import structlog
from openai import AsyncOpenAI

from app.core.config import settings

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are Teqa, an AI Business Intelligence Agent for Egyptian SMBs.
Your role is to analyze business metrics and generate actionable insights.

Rules:
- Be concise and actionable
- Focus on business impact
- No hallucinations - only reference provided data
- Use simple language that a busy business owner understands
- Include specific numbers and percentages
- Recommendations should be immediately actionable
- Keep responses under 3 sentences each
"""

REPORT_PROMPT = """Based on the following business metrics for {business_name} ({industry}):

Date: {report_date}
Revenue: {currency} {revenue:,.0f}
Orders: {orders_count}
Average Order Value: {currency} {avg_order_value:,.0f}
Revenue Growth: {growth_str}
Top Products: {top_products_str}

Previous day revenue: {currency} {prev_revenue:,.0f}

Generate exactly 3 items:
1. SUMMARY: A one-line summary of yesterday's performance
2. INSIGHT: One key business insight explaining WHY the numbers are what they are
3. RECOMMENDATION: One specific, actionable recommendation for today

Format your response as:
SUMMARY: ...
INSIGHT: ...
RECOMMENDATION: ...
"""


class InsightEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_insights(
        self,
        business_name: str,
        industry: str,
        currency: str,
        report_date: str,
        revenue: float,
        orders_count: int,
        avg_order_value: float,
        revenue_growth_pct: float | None,
        top_products: list[dict],
        prev_revenue: float,
    ) -> dict[str, str]:
        growth_str = f"{revenue_growth_pct:+.1f}%" if revenue_growth_pct else "N/A (no previous data)"
        top_products_str = ", ".join(
            [f"{p['name']} ({currency} {p['revenue']:,.0f})" for p in top_products[:3]]
        ) or "No sales data"

        prompt = REPORT_PROMPT.format(
            business_name=business_name,
            industry=industry,
            currency=currency,
            report_date=report_date,
            revenue=revenue,
            orders_count=orders_count,
            avg_order_value=avg_order_value,
            growth_str=growth_str,
            top_products_str=top_products_str,
            prev_revenue=prev_revenue,
        )

        if not self.client:
            logger.warning("OpenAI client not configured, using fallback insights")
            return self._fallback_insights(revenue, orders_count, revenue_growth_pct)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            content = response.choices[0].message.content or ""
            return self._parse_response(content)
        except Exception as e:
            logger.error("AI insight generation failed", error=str(e))
            return self._fallback_insights(revenue, orders_count, revenue_growth_pct)

    def _parse_response(self, content: str) -> dict[str, str]:
        result = {"summary": "", "insight": "", "recommendation": ""}
        for line in content.strip().split("\n"):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                result["summary"] = line[8:].strip()
            elif line.startswith("INSIGHT:"):
                result["insight"] = line[8:].strip()
            elif line.startswith("RECOMMENDATION:"):
                result["recommendation"] = line[15:].strip()
        return result

    def _fallback_insights(
        self, revenue: float, orders_count: int, growth_pct: float | None
    ) -> dict[str, str]:
        if growth_pct and growth_pct > 0:
            summary = f"Revenue grew {growth_pct:.1f}% with {orders_count} orders."
            insight = "Sales momentum is positive compared to the previous day."
            recommendation = "Maintain current strategy and focus on top sellers."
        elif growth_pct and growth_pct < 0:
            summary = f"Revenue declined {abs(growth_pct):.1f}% with {orders_count} orders."
            insight = "Sales dropped compared to the previous day."
            recommendation = "Consider running a promotion to boost today's sales."
        else:
            summary = f"Processed {orders_count} orders for total revenue."
            insight = "Steady performance with consistent order volume."
            recommendation = "Focus on customer retention and repeat purchases."

        return {"summary": summary, "insight": insight, "recommendation": recommendation}

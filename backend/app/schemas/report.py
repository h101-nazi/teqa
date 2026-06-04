from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    report_date: str
    status: str
    revenue: float
    orders_count: int
    avg_order_value: float
    revenue_growth_pct: float | None = None
    top_product: str | None = None
    ai_summary: str | None = None
    ai_insight: str | None = None
    ai_recommendation: str | None = None

    model_config = {"from_attributes": True}


class ReportDeliveryResponse(BaseModel):
    id: str
    status: str
    whatsapp_number: str
    sent_at: str | None = None
    delivered_at: str | None = None
    read_at: str | None = None

    model_config = {"from_attributes": True}


class DashboardOverview(BaseModel):
    total_revenue_today: float
    total_orders_today: int
    avg_order_value: float
    revenue_growth_pct: float | None
    reports_delivered: int
    active_integrations: int
    subscription_plan: str | None
    subscription_status: str | None

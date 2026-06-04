import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ReportStatus(StrEnum):
    PENDING = "pending"
    GENERATED = "generated"
    DELIVERED = "delivered"
    FAILED = "failed"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Report(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reports"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=ReportStatus.PENDING)

    # Metrics
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    orders_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_growth_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_product: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # AI content
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    whatsapp_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    business = relationship("Business", back_populates="reports")
    deliveries = relationship("ReportDelivery", back_populates="report", lazy="selectin")


class ReportDelivery(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "report_deliveries"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    whatsapp_number: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=DeliveryStatus.PENDING)
    whatsapp_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    report = relationship("Report", back_populates="deliveries")

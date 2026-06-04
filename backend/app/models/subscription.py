import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PlanType(StrEnum):
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INACTIVE = "inactive"


class Subscription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), unique=True
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(50), default=PlanType.STARTER)
    status: Mapped[str] = mapped_column(String(50), default=SubscriptionStatus.TRIALING)
    monthly_price: Mapped[float] = mapped_column(Float, default=499.0)
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    business = relationship("Business", back_populates="subscription")

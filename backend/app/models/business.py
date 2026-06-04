import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Business(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "businesses"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="Egypt")
    currency: Mapped[str] = mapped_column(String(10), default="EGP")
    whatsapp_number: Mapped[str] = mapped_column(String(20), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Africa/Cairo")
    is_onboarded: Mapped[bool] = mapped_column(default=False)

    # Relationships
    owner = relationship("User", back_populates="businesses")
    integrations = relationship("Integration", back_populates="business", lazy="selectin")
    transactions = relationship("Transaction", back_populates="business", lazy="noload")
    products = relationship("Product", back_populates="business", lazy="noload")
    customers = relationship("Customer", back_populates="business", lazy="noload")
    reports = relationship("Report", back_populates="business", lazy="noload")
    subscription = relationship("Subscription", back_populates="business", uselist=False)

import uuid
from enum import StrEnum

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class IntegrationType(StrEnum):
    SHOPIFY = "shopify"
    PAYMOB = "paymob"
    FAWRY = "fawry"
    CSV = "csv"
    POS = "pos"


class IntegrationStatus(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SYNCING = "syncing"


class Integration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integrations"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=IntegrationStatus.DISCONNECTED)
    credentials: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_sync_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    business = relationship("Business", back_populates="integrations")

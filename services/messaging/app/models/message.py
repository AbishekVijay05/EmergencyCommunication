# =============================================================================
# Message SQLAlchemy Model
# =============================================================================
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Text, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    recipient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    channel_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    encrypted_content: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(10), default="NORMAL",
        info={"check": "priority IN ('CRITICAL', 'HIGH', 'NORMAL', 'LOW')"}
    )
    message_type: Mapped[str] = mapped_column(
        String(20), default="direct",
        info={"check": "message_type IN ('direct', 'channel', 'broadcast')"}
    )
    iv: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

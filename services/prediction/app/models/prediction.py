# =============================================================================
# Prediction SQLAlchemy Models
# =============================================================================
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class PredictionRule(Base):
    __tablename__ = "prediction_rules"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition_expr: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_params: Mapped[dict] = mapped_column(JSONB, default=dict)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("prediction_rules.id"), nullable=True)
    event_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

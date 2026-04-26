# =============================================================================
# WBS + EVA SQLAlchemy Models
# =============================================================================
from __future__ import annotations
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Text, Integer, Date, ForeignKey, func, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class WBSItem(Base):
    __tablename__ = "wbs_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("wbs_items.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    planned_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    actual_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    earned_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    percent_complete: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="not_started")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EVASnapshot(Base):
    __tablename__ = "eva_snapshots"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_pv: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_ev: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_ac: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    spi: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    cpi: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    sv: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cv: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    eac: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

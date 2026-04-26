# =============================================================================
# Project Management Routes — WBS + EVA
# =============================================================================
from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db import get_db
from app.models.wbs import WBSItem, EVASnapshot

router = APIRouter()


class WBSUpdate(BaseModel):
    code: str = ""
    name: str = ""
    planned_value: float = 0
    actual_cost: float = 0
    earned_value: float = 0
    percent_complete: float = 0
    status: str = "not_started"


class EVAUpdate(BaseModel):
    wbs_item_id: str
    actual_cost: float = 0
    percent_complete: float = 0


@router.get("/wbs")
async def get_wbs(db: AsyncSession = Depends(get_db)):
    """Get Work Breakdown Structure."""
    result = await db.execute(select(WBSItem).order_by(WBSItem.code))
    items = result.scalars().all()
    return [
        {
            "id": str(i.id),
            "code": i.code,
            "name": i.name,
            "description": i.description,
            "planned_value": float(i.planned_value),
            "actual_cost": float(i.actual_cost),
            "earned_value": float(i.earned_value),
            "percent_complete": float(i.percent_complete),
            "status": i.status,
        }
        for i in items
    ]


@router.post("/wbs/tasks", status_code=201)
async def create_wbs_task(data: WBSUpdate, db: AsyncSession = Depends(get_db)):
    """Create or update a WBS task."""
    item = WBSItem(
        code=data.code,
        name=data.name,
        planned_value=Decimal(str(data.planned_value)),
        actual_cost=Decimal(str(data.actual_cost)),
        earned_value=Decimal(str(data.earned_value)),
        percent_complete=Decimal(str(data.percent_complete)),
        status=data.status,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return {"id": str(item.id), "status": "created"}


@router.get("/eva")
async def get_eva(db: AsyncSession = Depends(get_db)):
    """Calculate current EVA metrics from WBS data."""
    result = await db.execute(select(WBSItem))
    items = result.scalars().all()

    total_pv = sum(float(i.planned_value) for i in items)
    total_ac = sum(float(i.actual_cost) for i in items)
    total_ev = sum(float(i.planned_value) * float(i.percent_complete) / 100 for i in items)

    spi = total_ev / total_pv if total_pv > 0 else 0
    cpi = total_ev / total_ac if total_ac > 0 else 0
    sv = total_ev - total_pv
    cv = total_ev - total_ac
    bac = total_pv
    eac = bac / cpi if cpi > 0 else bac

    return {
        "total_pv": round(total_pv, 2),
        "total_ev": round(total_ev, 2),
        "total_ac": round(total_ac, 2),
        "spi": round(spi, 4),
        "cpi": round(cpi, 4),
        "sv": round(sv, 2),
        "cv": round(cv, 2),
        "bac": round(bac, 2),
        "eac": round(eac, 2),
        "status": "on_track" if spi >= 0.9 and cpi >= 0.9 else "at_risk" if spi >= 0.7 else "behind",
    }


@router.post("/eva/update")
async def update_eva(data: EVAUpdate, db: AsyncSession = Depends(get_db)):
    """Update progress for a WBS item and recalculate EVA."""
    from uuid import UUID
    result = await db.execute(select(WBSItem).where(WBSItem.id == UUID(data.wbs_item_id)))
    item = result.scalar_one_or_none()
    if not item:
        return {"error": "WBS item not found"}

    item.actual_cost = Decimal(str(data.actual_cost))
    item.percent_complete = Decimal(str(data.percent_complete))
    item.earned_value = item.planned_value * Decimal(str(data.percent_complete)) / 100

    if data.percent_complete >= 100:
        item.status = "completed"
    elif data.percent_complete > 0:
        item.status = "in_progress"

    await db.flush()
    return {"status": "updated", "item_id": str(item.id)}


@router.get("/eva/report")
async def eva_report(db: AsyncSession = Depends(get_db)):
    """Generate comprehensive EVA report."""
    # Get current metrics
    result = await db.execute(select(WBSItem).order_by(WBSItem.code))
    items = result.scalars().all()

    report_items = []
    for i in items:
        pv = float(i.planned_value)
        ac = float(i.actual_cost)
        ev = pv * float(i.percent_complete) / 100

        report_items.append({
            "code": i.code,
            "name": i.name,
            "pv": round(pv, 2),
            "ac": round(ac, 2),
            "ev": round(ev, 2),
            "percent_complete": float(i.percent_complete),
            "status": i.status,
            "spi": round(ev / pv, 4) if pv > 0 else 0,
            "cpi": round(ev / ac, 4) if ac > 0 else 0,
        })

    # Get historical snapshots
    snap_result = await db.execute(
        select(EVASnapshot).order_by(desc(EVASnapshot.snapshot_date)).limit(10)
    )
    snapshots = [
        {
            "date": str(s.snapshot_date),
            "pv": float(s.total_pv),
            "ev": float(s.total_ev),
            "ac": float(s.total_ac),
            "spi": float(s.spi) if s.spi else 0,
            "cpi": float(s.cpi) if s.cpi else 0,
        }
        for s in snap_result.scalars().all()
    ]

    return {"items": report_items, "history": snapshots}

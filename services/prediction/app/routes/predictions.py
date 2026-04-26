# =============================================================================
# Prediction Routes
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.config import get_settings
from app.models.prediction import PredictionRule, Prediction
from app.engines.rule_engine import RuleEngine
from shared.schemas import IncidentEvent

router = APIRouter()
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = RuleEngine(settings.redis_url)
    return _engine


@router.post("/evaluate")
async def evaluate_event(
    event: IncidentEvent,
    db: AsyncSession = Depends(get_db),
):
    """Evaluate an event against prediction rules."""
    engine = _get_engine()

    # Load active rules
    result = await db.execute(
        select(PredictionRule).where(PredictionRule.is_active == True).order_by(PredictionRule.priority.desc())
    )
    rules = [
        {
            "id": str(r.id),
            "name": r.name,
            "condition_expr": r.condition_expr,
            "action_type": r.action_type,
            "is_active": r.is_active,
        }
        for r in result.scalars().all()
    ]

    triggered = await engine.evaluate(event.model_dump(mode="json"), rules)

    # Persist predictions
    for t in triggered:
        pred = Prediction(
            rule_id=t["rule_id"] if t["rule_id"] else None,
            event_id=event.event_id,
            prediction_type=t["action_type"],
            confidence=t["confidence"],
            result=t,
            escalated=t["confidence"] > 0.8,
        )
        db.add(pred)
    await db.flush()

    return {"event_id": event.event_id, "triggered_rules": triggered, "count": len(triggered)}


@router.get("/latest")
async def latest_predictions(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get latest predictions."""
    result = await db.execute(
        select(Prediction).order_by(desc(Prediction.created_at)).limit(limit)
    )
    preds = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "event_id": p.event_id,
            "prediction_type": p.prediction_type,
            "confidence": p.confidence,
            "escalated": p.escalated,
            "result": p.result,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in preds
    ]


@router.get("/rules")
async def list_rules(db: AsyncSession = Depends(get_db)):
    """List all prediction rules."""
    result = await db.execute(select(PredictionRule).order_by(PredictionRule.priority.desc()))
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "condition_expr": r.condition_expr,
            "action_type": r.action_type,
            "priority": r.priority,
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.post("/rules")
async def create_rule(
    rule: dict,
    db: AsyncSession = Depends(get_db),
):
    """Create a new prediction rule."""
    new_rule = PredictionRule(
        name=rule["name"],
        description=rule.get("description"),
        condition_expr=rule["condition_expr"],
        action_type=rule["action_type"],
        priority=rule.get("priority", 0),
    )
    db.add(new_rule)
    await db.flush()
    await db.refresh(new_rule)
    return {"id": str(new_rule.id), "status": "created"}

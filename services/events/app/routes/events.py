# =============================================================================
# Events API Routes
# =============================================================================
from __future__ import annotations

import asyncio
import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.event import Event, AuditLog
from shared.schemas import IncidentEvent

router = APIRouter()


@router.post("/publish")
async def publish_event(event: IncidentEvent, request: Request):
    """Publish an event to Kafka."""
    from aiokafka import AIOKafkaProducer

    settings = request.app.state.settings
    start = time.perf_counter()

    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await producer.start()
        await producer.send_and_wait("incident-events", event.model_dump(mode="json"))
        await producer.stop()

        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "published", "event_id": event.event_id, "latency_ms": round(elapsed, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/history")
async def event_history(
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Query historical events with filtering."""
    query = select(Event).order_by(desc(Event.created_at))

    if event_type:
        query = query.where(Event.event_type == event_type)
    if severity:
        query = query.where(Event.severity == severity)
    if zone:
        query = query.where(Event.zone == zone)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    events = result.scalars().all()

    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "severity": e.severity,
            "location": e.location,
            "zone": e.zone,
            "source_node": e.source_node,
            "payload": e.payload,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


@router.get("/stream")
async def event_stream(request: Request):
    """Server-Sent Events stream of real-time events."""
    import redis.asyncio as aioredis

    settings = request.app.state.settings
    r = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def generate():
        pubsub = r.pubsub()
        await pubsub.subscribe("events:stream")
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield f"data: {message['data']}\n\n"
        except asyncio.CancelledError:
            await pubsub.unsubscribe("events:stream")
            await r.close()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/topics")
async def list_topics():
    """List available Kafka topics."""
    return {
        "topics": [
            {"name": "incident-events", "description": "Raw incident events from edge nodes"},
            {"name": "prediction-events", "description": "Prediction results from ML/rules"},
            {"name": "response-events", "description": "Protocol execution and response actions"},
            {"name": "audit-events", "description": "System activity audit trail"},
            {"name": "message-events", "description": "Message delivery events"},
        ]
    }


@router.get("/stats")
async def event_stats(db: AsyncSession = Depends(get_db)):
    """Get event statistics."""
    # Count by type
    type_counts = await db.execute(
        select(Event.event_type, func.count()).group_by(Event.event_type)
    )
    # Count by severity
    sev_counts = await db.execute(
        select(Event.severity, func.count()).group_by(Event.severity)
    )
    total = await db.execute(select(func.count()).select_from(Event))

    return {
        "total_events": total.scalar() or 0,
        "by_type": {row[0]: row[1] for row in type_counts.all()},
        "by_severity": {row[0]: row[1] for row in sev_counts.all()},
    }

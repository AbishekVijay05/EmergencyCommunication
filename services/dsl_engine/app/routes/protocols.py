# =============================================================================
# Protocol Routes — Parse, Validate, Execute, Audit
# =============================================================================
from __future__ import annotations

import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db import get_db
from app.models.protocol import Protocol, ProtocolExecution
from app.parser.dsl_parser import DSLParser
from app.executor.protocol_executor import ProtocolExecutor

router = APIRouter()
_parser = DSLParser()
_executor = ProtocolExecutor()


class DSLInput(BaseModel):
    dsl_source: str
    name: str = ""
    description: str = ""


class ExecuteInput(BaseModel):
    protocol_id: str = ""
    dsl_source: str = ""
    trigger_event: dict = {}


@router.post("/parse")
async def parse_dsl(data: DSLInput):
    """Parse DSL text and return structured protocol."""
    try:
        protocols = _parser.extract_protocols(data.dsl_source)
        return {"status": "parsed", "protocols": protocols, "count": len(protocols)}
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate")
async def validate_dsl(data: DSLInput):
    """Validate DSL syntax without executing."""
    result = _parser.validate(data.dsl_source)
    return result


@router.post("/execute")
async def execute_protocol(
    data: ExecuteInput,
    db: AsyncSession = Depends(get_db),
):
    """Execute a protocol (by ID or inline DSL source)."""
    start = time.perf_counter()

    # Get DSL source
    if data.protocol_id:
        result = await db.execute(
            select(Protocol).where(Protocol.id == UUID(data.protocol_id))
        )
        proto = result.scalar_one_or_none()
        if not proto:
            raise HTTPException(status_code=404, detail="Protocol not found")
        dsl_source = proto.dsl_source
    elif data.dsl_source:
        dsl_source = data.dsl_source
    else:
        raise HTTPException(status_code=400, detail="Provide protocol_id or dsl_source")

    # Parse
    try:
        protocols = _parser.extract_protocols(dsl_source)
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Execute all protocols
    all_results = []
    for proto_def in protocols:
        result = await _executor.execute(proto_def, data.trigger_event)
        all_results.append(result)

    elapsed = (time.perf_counter() - start) * 1000

    # Log execution
    execution = ProtocolExecution(
        protocol_id=UUID(data.protocol_id) if data.protocol_id else None,
        trigger_event_id=data.trigger_event.get("event_id"),
        status="completed",
        actions_executed=all_results,
        execution_time_ms=int(elapsed),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(execution)
    await db.flush()

    return {
        "status": "executed",
        "execution_id": str(execution.id),
        "results": all_results,
        "execution_time_ms": round(elapsed, 2),
    }


@router.get("")
async def list_protocols(db: AsyncSession = Depends(get_db)):
    """List all saved protocols."""
    result = await db.execute(
        select(Protocol).order_by(desc(Protocol.created_at))
    )
    protos = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "version": p.version,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in protos
    ]


@router.post("/save", status_code=201)
async def save_protocol(data: DSLInput, db: AsyncSession = Depends(get_db)):
    """Save a new protocol."""
    # Validate first
    validation = _parser.validate(data.dsl_source)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    compiled = _parser.extract_protocols(data.dsl_source)

    proto = Protocol(
        name=data.name or "Unnamed Protocol",
        description=data.description,
        dsl_source=data.dsl_source,
        compiled=compiled,
    )
    db.add(proto)
    await db.flush()
    await db.refresh(proto)

    return {"id": str(proto.id), "status": "saved"}


@router.get("/{protocol_id}/audit")
async def protocol_audit(
    protocol_id: str,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get execution audit log for a protocol."""
    result = await db.execute(
        select(ProtocolExecution)
        .where(ProtocolExecution.protocol_id == UUID(protocol_id))
        .order_by(desc(ProtocolExecution.started_at))
        .limit(limit)
    )
    execs = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "status": e.status,
            "actions_executed": e.actions_executed,
            "execution_time_ms": e.execution_time_ms,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in execs
    ]

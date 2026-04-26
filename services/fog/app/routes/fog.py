# =============================================================================
# Fog Node Routes
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, Request
from shared.schemas import IncidentEvent

router = APIRouter()


@router.get("/status")
async def fog_status(request: Request):
    """Get fog node status."""
    return {
        "node_id": request.app.state.settings.node_id,
        "role": request.app.state.settings.node_role,
        "router_stats": request.app.state.router.get_stats(),
        "consumer_stats": request.app.state.consumer.get_stats(),
    }


@router.post("/route")
async def route_message(message: dict, request: Request):
    """Route a message through the fog layer."""
    result = await request.app.state.router.route_message(message)
    return result


@router.post("/process-event")
async def process_event(event: IncidentEvent, request: Request):
    """Process an incident event."""
    result = await request.app.state.router.process_event(event.model_dump(mode="json"))
    return result

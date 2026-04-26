# =============================================================================
# Edge Node Routes
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, Request
from shared.schemas import IncidentEvent

router = APIRouter()


@router.get("/status")
async def node_status(request: Request):
    """Get edge node status and simulation stats."""
    simulator = request.app.state.simulator
    return {
        "node_id": request.app.state.settings.node_id,
        "zone": request.app.state.settings.zone,
        "stats": simulator.get_stats(),
    }


@router.post("/trigger")
async def trigger_incident(event: IncidentEvent, request: Request):
    """Manually trigger an incident event for testing."""
    simulator = request.app.state.simulator
    await simulator._publish_event(event)
    return {"status": "triggered", "event_id": event.event_id}


@router.get("/readings")
async def get_readings(request: Request):
    """Get latest sensor readings."""
    simulator = request.app.state.simulator
    readings = simulator._generate_sensor_readings()
    return {
        "node_id": request.app.state.settings.node_id,
        "readings": readings,
    }

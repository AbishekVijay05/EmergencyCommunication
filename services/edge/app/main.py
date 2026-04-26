# =============================================================================
# Edge Node — Main Application
# Simulates edge device: incident detection, sensor data, event publishing
# =============================================================================
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.simulator.incident_generator import IncidentSimulator
from app.routes.edge import router as edge_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    simulator = IncidentSimulator(settings)
    app.state.simulator = simulator
    app.state.settings = settings

    # Start background simulation
    task = asyncio.create_task(simulator.run())
    app.state.simulation_task = task

    print(f"📡 Edge node started | id={settings.node_id} zone={settings.zone}")
    yield

    task.cancel()
    await simulator.stop()
    print(f"🛑 Edge node {settings.node_id} shutting down")


app = FastAPI(
    title="Emergency Edge Node",
    description="Simulated edge node for incident detection and local messaging",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)
app.include_router(edge_router, prefix="/edge", tags=["Edge"])


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "edge",
        "node_id": settings.node_id,
        "zone": settings.zone,
    }

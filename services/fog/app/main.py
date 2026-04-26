# =============================================================================
# Fog Node — Main Application
# Message routing, protocol execution, incident coordination
# =============================================================================
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.services.message_router import MessageRouter
from app.consumer.event_consumer import EventConsumer
from app.routes.fog import router as fog_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    router_service = MessageRouter(settings)
    consumer = EventConsumer(settings)
    app.state.router = router_service
    app.state.consumer = consumer
    app.state.settings = settings

    # Start Kafka consumer in background
    consumer_task = asyncio.create_task(consumer.run())
    app.state.consumer_task = consumer_task

    print(f"🌫️ Fog node started | id={settings.node_id} role={settings.node_role}")
    yield

    consumer_task.cancel()
    await consumer.stop()
    print(f"🛑 Fog node {settings.node_id} shutting down")


app = FastAPI(
    title="Emergency Fog Node",
    description="Fog layer coordinator: message routing, protocol execution, encryption",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)
app.include_router(fog_router, prefix="/fog", tags=["Fog"])


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "fog",
        "node_id": settings.node_id,
        "role": settings.node_role,
    }

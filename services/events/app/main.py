# =============================================================================
# Events Service — EDA Pipeline
# Event publishing, consuming, processing, and history
# =============================================================================
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.db import init_db
from app.consumers.incident_consumer import IncidentConsumer
from app.routes.events import router as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()

    consumer = IncidentConsumer(settings)
    consumer_task = asyncio.create_task(consumer.run())
    app.state.consumer = consumer
    app.state.settings = settings

    print(f"📡 Events service started | env={settings.environment}")
    yield

    consumer_task.cancel()
    await consumer.stop()
    print("🛑 Events service shutting down")


app = FastAPI(
    title="Emergency Events Service",
    description="Event-Driven Architecture pipeline for incident management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
app.include_router(events_router, prefix="/events", tags=["Events"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "events"}

# =============================================================================
# Messaging Service — Main Application
# Encrypted messaging, channels, broadcast, WebSocket
# =============================================================================
from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.db import init_db
from app.routes.messages import router as messages_router
from app.websocket.handler import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    print(f"📨 Messaging service started | env={settings.environment}")
    yield
    print("🛑 Messaging service shutting down")


app = FastAPI(
    title="Emergency Messaging Service",
    description="Encrypted emergency messaging with channels and broadcast",
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

app.include_router(messages_router, prefix="/messages", tags=["Messages"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "messaging"}

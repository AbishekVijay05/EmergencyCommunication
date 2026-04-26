# =============================================================================
# API Gateway — Main Application
# Reverse proxy + auth middleware + rate limiting
# =============================================================================
from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import Settings, get_settings
from app.middleware.auth import verify_token, get_current_user
from app.routes import health, proxy


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    settings = get_settings()
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.settings = settings
    print(f"🚀 Gateway started | env={settings.environment}")
    yield
    await app.state.http_client.aclose()
    print("🛑 Gateway shutting down")


app = FastAPI(
    title="Emergency Communication Gateway",
    description="API Gateway for the Emergency Edge/Fog Communication System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time-Ms"] = f"{elapsed:.2f}"
    return response

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(proxy.router, prefix="/api", tags=["Proxy"])

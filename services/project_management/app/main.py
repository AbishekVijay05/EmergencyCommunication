# =============================================================================
# Project Management Service — WBS + EVA
# =============================================================================
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import get_settings
from app.db import init_db
from app.routes.project import router as project_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    print(f"📊 Project Management started | env={settings.environment}")
    yield
    print("🛑 Project Management shutting down")

app = FastAPI(
    title="Emergency Project Management",
    description="WBS and EVA tracking for the emergency communication system",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)
app.include_router(project_router, prefix="/project", tags=["Project Management"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "project_management"}

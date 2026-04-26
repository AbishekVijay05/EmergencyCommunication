# =============================================================================
# Prediction Service — Main Application
# =============================================================================
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import get_settings
from app.db import init_db
from app.routes.predictions import router as pred_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    print(f"🧠 Prediction service started | env={settings.environment}")
    yield
    print("🛑 Prediction service shutting down")

app = FastAPI(
    title="Emergency Prediction Service",
    description="Rule-based and ML incident prediction engine",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)
app.include_router(pred_router, prefix="/predictions", tags=["Predictions"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "prediction"}

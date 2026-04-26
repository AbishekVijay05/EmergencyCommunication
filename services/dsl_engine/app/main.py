# =============================================================================
# DSL Engine — Main Application
# =============================================================================
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import get_settings
from app.db import init_db
from app.routes.protocols import router as proto_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    print(f"📜 DSL Engine started | env={settings.environment}")
    yield
    print("🛑 DSL Engine shutting down")

app = FastAPI(
    title="Emergency DSL Engine",
    description="Domain-Specific Language parser and executor for emergency protocols",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)
app.include_router(proto_router, prefix="/protocols", tags=["Protocols"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "dsl_engine"}

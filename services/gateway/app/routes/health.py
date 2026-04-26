# =============================================================================
# Health Check Routes
# =============================================================================
from __future__ import annotations

import time
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health", summary="System health check")
async def health_check(request: Request):
    """Return system health status with service connectivity."""
    settings = request.app.state.settings
    client = request.app.state.http_client

    services = {
        "auth": settings.auth_service_url,
        "messaging": settings.messaging_service_url,
        "events": settings.events_service_url,
        "prediction": settings.prediction_service_url,
        "dsl_engine": settings.dsl_service_url,
        "project_management": settings.project_service_url,
    }

    status_checks = {}
    for name, url in services.items():
        try:
            start = time.perf_counter()
            resp = await client.get(f"{url}/health", timeout=5.0)
            latency = (time.perf_counter() - start) * 1000
            status_checks[name] = {
                "status": "healthy" if resp.status_code == 200 else "unhealthy",
                "latency_ms": round(latency, 2),
            }
        except Exception:
            status_checks[name] = {"status": "unreachable", "latency_ms": -1}

    all_healthy = all(s["status"] == "healthy" for s in status_checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "gateway",
        "version": "1.0.0",
        "services": status_checks,
    }

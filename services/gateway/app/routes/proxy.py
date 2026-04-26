# =============================================================================
# Reverse Proxy Routes — Forward requests to backend services
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, Request, Response, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.config import get_settings, Settings

router = APIRouter()

SERVICE_MAP = {
    "auth": "auth_service_url",
    "messages": "messaging_service_url",
    "channels": "messaging_service_url",
    "events": "events_service_url",
    "predictions": "prediction_service_url",
    "protocols": "dsl_service_url",
    "project": "project_service_url",
}


@router.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    summary="Proxy requests to backend services",
)
async def proxy_request(
    service: str,
    path: str,
    request: Request,
    user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Forward authenticated requests to the appropriate backend service."""
    service_attr = SERVICE_MAP.get(service)
    if not service_attr:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service}")

    base_url = getattr(settings, service_attr)
    target_url = f"{base_url}/{path}"

    client = request.app.state.http_client

    # Forward request with user context headers
    headers = {
        "X-User-Id": user["user_id"],
        "X-User-Role": user["role"],
        "Content-Type": request.headers.get("Content-Type", "application/json"),
    }

    body = await request.body()

    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Service unavailable: {e}")


# Public routes (no auth required)
@router.post("/auth/login", summary="Login (no auth required)")
async def proxy_login(request: Request, settings: Settings = Depends(get_settings)):
    """Forward login request without authentication."""
    client = request.app.state.http_client
    body = await request.body()
    try:
        response = await client.post(
            f"{settings.auth_service_url}/auth/login",
            content=body,
            headers={"Content-Type": "application/json"},
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Auth service unavailable: {e}")


@router.post("/auth/register", summary="Register (no auth required)")
async def proxy_register(request: Request, settings: Settings = Depends(get_settings)):
    """Forward registration request without authentication."""
    client = request.app.state.http_client
    body = await request.body()
    try:
        response = await client.post(
            f"{settings.auth_service_url}/auth/register",
            content=body,
            headers={"Content-Type": "application/json"},
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Auth service unavailable: {e}")

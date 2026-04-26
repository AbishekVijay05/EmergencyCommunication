# =============================================================================
# Message Router — Routes messages between edge, fog, and cloud
# =============================================================================
from __future__ import annotations

import json
import time
from collections import defaultdict

import httpx
import redis.asyncio as aioredis

from app.config import Settings
from services.security.aes_cipher import AESCipher


class MessageRouter:
    """Fog-layer message routing with encryption and prioritization."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        self._http = httpx.AsyncClient(timeout=10.0)
        self._cipher = AESCipher()
        self._stats = {
            "messages_routed": 0,
            "critical_bypassed": 0,
            "avg_latency_ms": 0.0,
        }
        self._latencies: list[float] = []

    async def route_message(self, message: dict) -> dict:
        """Route a message based on priority and destination."""
        start = time.perf_counter()

        priority = message.get("priority", "NORMAL")

        # Critical messages skip queue — direct routing
        if priority == "CRITICAL":
            result = await self._route_critical(message)
            self._stats["critical_bypassed"] += 1
        else:
            result = await self._route_normal(message)

        elapsed = (time.perf_counter() - start) * 1000
        self._latencies.append(elapsed)
        self._stats["messages_routed"] += 1
        self._stats["avg_latency_ms"] = sum(self._latencies) / len(self._latencies)

        return result

    async def _route_critical(self, message: dict) -> dict:
        """Route critical messages directly, bypassing normal queue."""
        # Forward to messaging service immediately
        try:
            response = await self._http.post(
                f"{self.settings.messaging_service_url}/messages/broadcast",
                json={
                    "content": message.get("content", "CRITICAL ALERT"),
                    "priority": "CRITICAL",
                },
                headers={"X-User-Id": message.get("sender_id", "system")},
            )
            return {"status": "routed", "priority": "CRITICAL", "response": response.status_code}
        except Exception as e:
            # Buffer in Redis for retry
            await self._buffer_message(message)
            return {"status": "buffered", "error": str(e)}

    async def _route_normal(self, message: dict) -> dict:
        """Route normal messages through the standard queue."""
        try:
            await self._redis.rpush(
                f"fog:message_queue:{self.settings.node_id}",
                json.dumps(message),
            )
            return {"status": "queued"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _buffer_message(self, message: dict):
        """Buffer message in Redis for later delivery."""
        await self._redis.rpush(
            f"fog:buffer:{self.settings.node_id}",
            json.dumps(message),
        )

    async def process_event(self, event: dict) -> dict:
        """Process an incoming event from edge nodes."""
        severity = event.get("severity", "low")
        event_type = event.get("event_type", "unknown")

        # Forward to prediction service
        try:
            await self._http.post(
                f"{self.settings.prediction_service_url}/predictions/evaluate",
                json=event,
            )
        except Exception:
            pass

        # If high severity, trigger DSL protocol execution
        if severity in ("high", "critical"):
            try:
                await self._http.post(
                    f"{self.settings.dsl_service_url}/protocols/execute",
                    json={"trigger_event": event},
                )
            except Exception:
                pass

        return {"status": "processed", "event_type": event_type, "severity": severity}

    def get_stats(self) -> dict:
        return {
            **self._stats,
            "node_id": self.settings.node_id,
            "role": self.settings.node_role,
        }

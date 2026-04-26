# =============================================================================
# Rule Engine — Configurable rule-based incident prediction
# =============================================================================
from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Any

import redis.asyncio as aioredis


class RuleEngine:
    """Rule-based prediction engine with event correlation."""

    def __init__(self, redis_url: str):
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._event_counts: dict[str, int] = defaultdict(int)
        self._stats = {"evaluations": 0, "triggers": 0}

    async def evaluate(self, event: dict, rules: list[dict]) -> list[dict]:
        """Evaluate an event against all active rules."""
        start = time.perf_counter()
        triggered = []

        # Update event counts
        event_type = event.get("event_type", "unknown")
        severity = event.get("severity", "low")
        zone = event.get("zone", "unknown")

        await self._update_counters(event_type, zone)
        repeated_events = await self._get_repeat_count(event_type, zone)
        event_count_5min = await self._get_event_count_5min(zone)

        context = {
            "event_type": event_type,
            "severity": severity,
            "zone": zone,
            "repeated_events": repeated_events,
            "event_count_last_5min": event_count_5min,
            "concurrent_network_failure": await self._check_concurrent("network_failure", zone),
        }

        for rule in rules:
            if not rule.get("is_active", True):
                continue

            condition = rule.get("condition_expr", "")
            if self._evaluate_condition(condition, context):
                triggered.append({
                    "rule_id": str(rule.get("id", "")),
                    "rule_name": rule.get("name", ""),
                    "action_type": rule.get("action_type", ""),
                    "confidence": self._calculate_confidence(context, rule),
                    "context": context,
                })
                self._stats["triggers"] += 1

        self._stats["evaluations"] += 1
        elapsed = (time.perf_counter() - start) * 1000

        return triggered

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        """Evaluate a rule condition against event context.

        Supports: ==, !=, >, <, >=, <=, IN, AND, OR
        """
        try:
            # Replace variables with context values
            expr = condition
            for key, value in context.items():
                if isinstance(value, str):
                    expr = expr.replace(key, f'"{value}"')
                elif isinstance(value, bool):
                    expr = expr.replace(key, str(value).lower())
                else:
                    expr = expr.replace(key, str(value))

            # Safe evaluation (limited to comparisons)
            expr = expr.replace("AND", "and").replace("OR", "or")
            expr = expr.replace("IN", "in")
            expr = expr.replace("true", "True").replace("false", "False")

            return bool(eval(expr, {"__builtins__": {}}, {}))
        except Exception:
            return False

    def _calculate_confidence(self, context: dict, rule: dict) -> float:
        """Calculate confidence score based on event context."""
        confidence = 0.5
        severity = context.get("severity", "low")
        repeated = context.get("repeated_events", 0)

        severity_weights = {"critical": 0.95, "high": 0.80, "medium": 0.60, "low": 0.40}
        confidence = severity_weights.get(severity, 0.5)

        if repeated > 5:
            confidence = min(confidence + 0.15, 1.0)
        elif repeated > 3:
            confidence = min(confidence + 0.10, 1.0)

        return round(confidence, 3)

    async def _update_counters(self, event_type: str, zone: str):
        """Update event counters in Redis."""
        try:
            key = f"prediction:count:{zone}:{event_type}"
            await self._redis.incr(key)
            await self._redis.expire(key, 300)  # 5 min TTL

            ts_key = f"prediction:events_5min:{zone}"
            await self._redis.incr(ts_key)
            await self._redis.expire(ts_key, 300)
        except Exception:
            pass

    async def _get_repeat_count(self, event_type: str, zone: str) -> int:
        try:
            val = await self._redis.get(f"prediction:count:{zone}:{event_type}")
            return int(val) if val else 0
        except Exception:
            return 0

    async def _get_event_count_5min(self, zone: str) -> int:
        try:
            val = await self._redis.get(f"prediction:events_5min:{zone}")
            return int(val) if val else 0
        except Exception:
            return 0

    async def _check_concurrent(self, event_type: str, zone: str) -> bool:
        try:
            val = await self._redis.get(f"prediction:count:{zone}:{event_type}")
            return int(val) > 0 if val else False
        except Exception:
            return False

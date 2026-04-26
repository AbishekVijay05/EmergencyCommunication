# =============================================================================
# Shared Utilities — Latency Timing Decorator
# =============================================================================
from __future__ import annotations

import time
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class LatencyTracker:
    """Track and report operation latencies."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._measurements: dict[str, list[float]] = {}

    def track(self, operation: str) -> Callable:
        """Decorator to track operation latency."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    self._record(operation, elapsed_ms)

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    self._record(operation, elapsed_ms)

            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator

    def _record(self, operation: str, elapsed_ms: float) -> None:
        """Record a latency measurement."""
        if operation not in self._measurements:
            self._measurements[operation] = []
        self._measurements[operation].append(elapsed_ms)

        # Log if exceeding thresholds
        thresholds = {
            "message_send": 100,
            "event_process": 200,
            "encryption": 50,
            "protocol_execute": 500,
        }
        threshold = thresholds.get(operation, 500)
        if elapsed_ms > threshold:
            logger.warning(
                f"[{self.service_name}] {operation} latency {elapsed_ms:.1f}ms "
                f"exceeds threshold {threshold}ms"
            )

    def get_stats(self, operation: str) -> dict[str, float]:
        """Get latency statistics for an operation."""
        measurements = self._measurements.get(operation, [])
        if not measurements:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0, "p99_ms": 0}

        sorted_m = sorted(measurements)
        p99_idx = max(0, int(len(sorted_m) * 0.99) - 1)

        return {
            "count": len(measurements),
            "avg_ms": round(sum(measurements) / len(measurements), 2),
            "min_ms": round(sorted_m[0], 2),
            "max_ms": round(sorted_m[-1], 2),
            "p99_ms": round(sorted_m[p99_idx], 2),
        }

    def get_all_stats(self) -> dict[str, dict[str, float]]:
        """Get stats for all tracked operations."""
        return {op: self.get_stats(op) for op in self._measurements}

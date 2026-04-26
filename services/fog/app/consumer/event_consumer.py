# =============================================================================
# Kafka Event Consumer — Consumes events from edge nodes
# =============================================================================
from __future__ import annotations

import asyncio
import json

from app.config import Settings


class EventConsumer:
    """Consumes incident events from Kafka and coordinates response."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._consumer = None
        self._running = False
        self._stats = {"events_consumed": 0, "errors": 0}

    async def run(self):
        """Start consuming events from Kafka."""
        from aiokafka import AIOKafkaConsumer

        self._running = True
        try:
            self._consumer = AIOKafkaConsumer(
                "incident-events",
                bootstrap_servers=self.settings.kafka_bootstrap_servers,
                group_id=f"fog-{self.settings.node_id}",
                auto_offset_reset="latest",
                value_deserializer=lambda v: json.loads(v.decode()),
            )
            await self._consumer.start()
            print(f"🎯 [{self.settings.node_id}] Kafka consumer started")

            async for msg in self._consumer:
                if not self._running:
                    break
                try:
                    event = msg.value
                    await self._handle_event(event)
                    self._stats["events_consumed"] += 1
                except Exception as e:
                    self._stats["errors"] += 1
                    print(f"❌ Event processing error: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"⚠️ Kafka consumer error: {e}")
        finally:
            if self._consumer:
                await self._consumer.stop()

    async def stop(self):
        self._running = False

    async def _handle_event(self, event: dict):
        """Process incoming event."""
        severity = event.get("severity", "low")
        event_type = event.get("event_type", "unknown")
        source = event.get("source_node", "unknown")

        print(f"📥 [{self.settings.node_id}] Event received: "
              f"{event_type} severity={severity} from={source}")

        # Coordinate based on severity
        if severity in ("critical", "high"):
            print(f"🚨 [{self.settings.node_id}] HIGH PRIORITY: Initiating coordination for {event_type}")

    def get_stats(self) -> dict:
        return self._stats

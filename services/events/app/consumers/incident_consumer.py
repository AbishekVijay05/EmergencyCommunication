# =============================================================================
# Incident Event Consumer — Persists events from Kafka to DB
# =============================================================================
from __future__ import annotations

import asyncio
import json

from app.config import Settings


class IncidentConsumer:
    """Consumes incident events and persists them to the database."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._running = False
        self._stats = {"consumed": 0, "persisted": 0, "errors": 0}

    async def run(self):
        from aiokafka import AIOKafkaConsumer
        from app.db import async_session
        from app.models.event import Event

        self._running = True
        try:
            consumer = AIOKafkaConsumer(
                "incident-events", "prediction-events", "response-events",
                bootstrap_servers=self.settings.kafka_bootstrap_servers,
                group_id="events-service",
                auto_offset_reset="latest",
                value_deserializer=lambda v: json.loads(v.decode()),
            )
            await consumer.start()
            print("📥 Events consumer started")

            async for msg in consumer:
                if not self._running:
                    break
                try:
                    data = msg.value
                    self._stats["consumed"] += 1

                    async with async_session() as session:
                        event = Event(
                            event_id=data.get("event_id", str(self._stats["consumed"])),
                            event_type=data.get("event_type", "unknown"),
                            severity=data.get("severity", "low"),
                            location=data.get("location"),
                            zone=data.get("zone"),
                            source_node=data.get("source_node"),
                            payload=data.get("metadata", {}),
                        )
                        session.add(event)
                        await session.commit()
                        self._stats["persisted"] += 1

                except Exception as e:
                    self._stats["errors"] += 1
                    print(f"❌ Event persistence error: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"⚠️ Events consumer error: {e}")

    async def stop(self):
        self._running = False

    def get_stats(self) -> dict:
        return self._stats

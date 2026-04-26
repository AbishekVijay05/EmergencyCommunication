# =============================================================================
# Incident Simulator — Generates realistic sensor data and incidents
# =============================================================================
from __future__ import annotations

import asyncio
import json
import random
import time
from datetime import datetime, timezone

import redis.asyncio as aioredis

from app.config import Settings
from shared.schemas import IncidentEvent, EventType, Severity


class IncidentSimulator:
    """Simulates edge-node sensor data and incident detection."""

    SENSOR_CONFIGS = {
        "temperature": {"min": 15, "max": 45, "alert_threshold": 38, "unit": "°C"},
        "smoke": {"min": 0, "max": 100, "alert_threshold": 60, "unit": "ppm"},
        "motion": {"min": 0, "max": 10, "alert_threshold": 7, "unit": "events/s"},
        "network": {"min": 0, "max": 100, "alert_threshold": 20, "unit": "% loss"},
        "access": {"min": 0, "max": 5, "alert_threshold": 3, "unit": "violations"},
    }

    EVENT_MAP = {
        "temperature": EventType.FIRE_ALERT,
        "smoke": EventType.FIRE_ALERT,
        "motion": EventType.INTRUSION_DETECTED,
        "network": EventType.NETWORK_FAILURE,
        "access": EventType.INTRUSION_DETECTED,
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.sensors = settings.sensors.split(",")
        self._running = False
        self._producer = None
        self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        self._event_buffer: list[dict] = []
        self._stats = {"events_generated": 0, "alerts_triggered": 0}

    async def _init_kafka(self):
        """Initialize Kafka producer."""
        from aiokafka import AIOKafkaProducer
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        try:
            await self._producer.start()
        except Exception as e:
            print(f"⚠️ Kafka unavailable, buffering events: {e}")
            self._producer = None

    async def run(self):
        """Main simulation loop."""
        self._running = True
        await self._init_kafka()

        while self._running:
            try:
                readings = self._generate_sensor_readings()
                incidents = self._detect_incidents(readings)

                for incident in incidents:
                    await self._publish_event(incident)
                    self._stats["alerts_triggered"] += 1

                # Store latest readings in Redis
                await self._store_readings(readings)
                self._stats["events_generated"] += 1

                await asyncio.sleep(self.settings.simulation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                await asyncio.sleep(2)

    async def stop(self):
        """Stop simulation and cleanup."""
        self._running = False
        if self._producer:
            await self._producer.stop()
        await self._redis.close()

    def _generate_sensor_readings(self) -> dict:
        """Generate realistic sensor readings with occasional anomalies."""
        readings = {}
        for sensor in self.sensors:
            config = self.SENSOR_CONFIGS.get(sensor, {"min": 0, "max": 100, "alert_threshold": 80})

            # Normal distribution with occasional spikes
            if random.random() < 0.1:  # 10% chance of anomaly
                value = random.uniform(config["alert_threshold"], config["max"])
            else:
                center = (config["min"] + config["alert_threshold"]) / 2
                value = random.gauss(center, (config["alert_threshold"] - config["min"]) / 3)
                value = max(config["min"], min(config["max"], value))

            readings[sensor] = round(value, 2)

        return readings

    def _detect_incidents(self, readings: dict) -> list[IncidentEvent]:
        """Detect incidents from sensor readings."""
        incidents = []

        for sensor, value in readings.items():
            config = self.SENSOR_CONFIGS.get(sensor, {})
            threshold = config.get("alert_threshold", 80)

            if value >= threshold:
                severity = self._calculate_severity(value, threshold, config.get("max", 100))
                event = IncidentEvent(
                    event_type=self.EVENT_MAP.get(sensor, EventType.FIRE_ALERT),
                    severity=severity,
                    location=f"{self.settings.zone}-{sensor}",
                    zone=self.settings.zone,
                    source_node=self.settings.node_id,
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "sensor": sensor,
                        "value": value,
                        "threshold": threshold,
                        "unit": config.get("unit", ""),
                    },
                )
                incidents.append(event)

        return incidents

    def _calculate_severity(self, value: float, threshold: float, max_val: float) -> Severity:
        """Calculate severity based on how far above threshold."""
        ratio = (value - threshold) / (max_val - threshold) if max_val > threshold else 0
        if ratio > 0.8:
            return Severity.CRITICAL
        elif ratio > 0.5:
            return Severity.HIGH
        elif ratio > 0.2:
            return Severity.MEDIUM
        return Severity.LOW

    async def _publish_event(self, event: IncidentEvent):
        """Publish event to Kafka or buffer locally."""
        event_data = event.model_dump(mode="json")

        if self._producer:
            try:
                await self._producer.send_and_wait("incident-events", event_data)
                print(f"🔥 [{self.settings.node_id}] Alert: {event.event_type.value} "
                      f"severity={event.severity.value} zone={event.zone}")
            except Exception:
                self._event_buffer.append(event_data)
                await self._buffer_to_redis(event_data)
        else:
            self._event_buffer.append(event_data)
            await self._buffer_to_redis(event_data)

    async def _buffer_to_redis(self, event_data: dict):
        """Buffer events in Redis when Kafka is unavailable."""
        try:
            await self._redis.lpush(
                f"edge:buffer:{self.settings.node_id}",
                json.dumps(event_data),
            )
        except Exception:
            pass

    async def _store_readings(self, readings: dict):
        """Store latest sensor readings in Redis."""
        try:
            await self._redis.hset(
                f"edge:readings:{self.settings.node_id}",
                mapping={k: str(v) for k, v in readings.items()},
            )
        except Exception:
            pass

    def get_stats(self) -> dict:
        return {
            **self._stats,
            "node_id": self.settings.node_id,
            "zone": self.settings.zone,
            "sensors": self.sensors,
            "buffer_size": len(self._event_buffer),
        }

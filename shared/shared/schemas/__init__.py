# =============================================================================
# Shared Pydantic Schemas — Event Models
# =============================================================================
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    FIRE_ALERT = "fire_alert"
    MEDICAL_EMERGENCY = "medical_emergency"
    INTRUSION_DETECTED = "intrusion_detected"
    NETWORK_FAILURE = "network_failure"
    EVACUATION_REQUIRED = "evacuation_required"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentEvent(BaseModel):
    """Core event schema used across all services."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    severity: Severity
    location: str = ""
    zone: str = ""
    source_node: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PredictionEvent(BaseModel):
    """Prediction result event."""
    prediction_id: str = Field(default_factory=lambda: str(uuid4()))
    source_event_id: str
    prediction_type: str
    confidence: float = 0.0
    action: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponseEvent(BaseModel):
    """Protocol execution / response event."""
    response_id: str = Field(default_factory=lambda: str(uuid4()))
    trigger_event_id: str
    protocol_id: Optional[str] = None
    actions_taken: list[str] = Field(default_factory=list)
    status: str = "completed"
    execution_time_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(BaseModel):
    """Audit trail event."""
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    action: str
    entity_type: str = ""
    entity_id: str = ""
    actor_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

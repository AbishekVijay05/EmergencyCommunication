# =============================================================================
# Shared Pydantic Schemas — Message Models
# =============================================================================
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MessagePriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class MessageType(str, Enum):
    DIRECT = "direct"
    CHANNEL = "channel"
    BROADCAST = "broadcast"


class MessageSend(BaseModel):
    """Schema for sending a message."""
    recipient_id: Optional[str] = None
    channel_id: Optional[str] = None
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    message_type: MessageType = MessageType.DIRECT


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    sender_id: str
    recipient_id: Optional[str] = None
    channel_id: Optional[str] = None
    content: str
    priority: MessagePriority
    message_type: MessageType
    acknowledged: bool = False
    created_at: datetime


class MessageAck(BaseModel):
    """Schema for message acknowledgement."""
    message_id: str


class BroadcastMessage(BaseModel):
    """Schema for emergency broadcast."""
    content: str
    priority: MessagePriority = MessagePriority.CRITICAL
    zone: Optional[str] = None


class ChannelCreate(BaseModel):
    """Schema for creating a channel."""
    name: str
    description: str = ""
    incident_type: str = ""


class ChannelResponse(BaseModel):
    """Schema for channel response."""
    id: str
    name: str
    description: str
    incident_type: str
    is_active: bool
    member_count: int = 0
    created_at: datetime

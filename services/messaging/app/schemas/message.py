# =============================================================================
# Messaging Pydantic Schemas
# =============================================================================
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MessageSend(BaseModel):
    recipient_id: Optional[str] = None
    channel_id: Optional[str] = None
    content: str
    priority: str = "NORMAL"
    message_type: str = "direct"


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    recipient_id: Optional[str] = None
    channel_id: Optional[str] = None
    content: str
    priority: str
    message_type: str
    acknowledged: bool = False
    delivered: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class MessageAck(BaseModel):
    message_id: str


class BroadcastRequest(BaseModel):
    content: str
    priority: str = "CRITICAL"
    zone: Optional[str] = None


class ChannelCreate(BaseModel):
    name: str
    description: str = ""
    incident_type: str = ""


class ChannelResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    incident_type: Optional[str] = None
    is_active: bool
    member_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

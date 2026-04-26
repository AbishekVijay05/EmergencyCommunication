# =============================================================================
# Message Routes — Send, History, Broadcast, Ack
# =============================================================================
from __future__ import annotations

import os
import sys
import time
import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.db import get_db
from app.config import get_settings, Settings
from app.models.message import Message
from app.schemas.message import MessageSend, MessageResponse, MessageAck, BroadcastRequest
from services.security.aes_cipher import AESCipher, EncryptedPayload

router = APIRouter()

# Shared encryption key (in production, use per-session keys via key exchange)
_cipher = None


def _get_cipher() -> AESCipher:
    global _cipher
    if _cipher is None:
        _cipher = AESCipher()
    return _cipher


@router.post("/send", response_model=MessageResponse, status_code=201)
async def send_message(
    data: MessageSend,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Send an encrypted message to a user or channel."""
    start = time.perf_counter()
    cipher = _get_cipher()

    # Encrypt the message content
    encrypted = cipher.encrypt(data.content)

    message = Message(
        sender_id=UUID(x_user_id),
        recipient_id=UUID(data.recipient_id) if data.recipient_id else None,
        channel_id=UUID(data.channel_id) if data.channel_id else None,
        encrypted_content=encrypted.ciphertext,
        priority=data.priority,
        message_type=data.message_type,
        iv=encrypted.iv,
        tag=encrypted.tag,
    )

    db.add(message)
    await db.flush()
    await db.refresh(message)

    elapsed = (time.perf_counter() - start) * 1000
    print(f"📨 Message sent in {elapsed:.1f}ms | priority={data.priority}")

    return MessageResponse(
        id=str(message.id),
        sender_id=str(message.sender_id),
        recipient_id=str(message.recipient_id) if message.recipient_id else None,
        channel_id=str(message.channel_id) if message.channel_id else None,
        content=data.content,  # Return decrypted to sender
        priority=message.priority,
        message_type=message.message_type,
        acknowledged=message.acknowledged,
        delivered=message.delivered,
        created_at=message.created_at,
    )


@router.get("/history", response_model=list[MessageResponse])
async def message_history(
    x_user_id: str = Header(..., alias="X-User-Id"),
    channel_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Get message history for the current user or a channel."""
    cipher = _get_cipher()
    user_id = UUID(x_user_id)

    if channel_id:
        query = (
            select(Message)
            .where(Message.channel_id == UUID(channel_id))
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
    else:
        query = (
            select(Message)
            .where(
                or_(Message.sender_id == user_id, Message.recipient_id == user_id)
            )
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )

    result = await db.execute(query)
    messages = result.scalars().all()

    responses = []
    for msg in messages:
        # Decrypt message content
        try:
            payload = EncryptedPayload(
                ciphertext=msg.encrypted_content,
                iv=msg.iv,
                tag=msg.tag,
            )
            decrypted = cipher.decrypt(payload)
        except Exception:
            decrypted = "[DECRYPTION FAILED]"

        responses.append(MessageResponse(
            id=str(msg.id),
            sender_id=str(msg.sender_id),
            recipient_id=str(msg.recipient_id) if msg.recipient_id else None,
            channel_id=str(msg.channel_id) if msg.channel_id else None,
            content=decrypted,
            priority=msg.priority,
            message_type=msg.message_type,
            acknowledged=msg.acknowledged,
            delivered=msg.delivered,
            created_at=msg.created_at,
        ))

    return responses


@router.post("/broadcast", response_model=MessageResponse, status_code=201)
async def broadcast_message(
    data: BroadcastRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Send an emergency broadcast to all responders."""
    cipher = _get_cipher()
    encrypted = cipher.encrypt(data.content)

    message = Message(
        sender_id=UUID(x_user_id),
        encrypted_content=encrypted.ciphertext,
        priority=data.priority,
        message_type="broadcast",
        iv=encrypted.iv,
        tag=encrypted.tag,
    )

    db.add(message)
    await db.flush()
    await db.refresh(message)

    return MessageResponse(
        id=str(message.id),
        sender_id=str(message.sender_id),
        content=data.content,
        priority=message.priority,
        message_type="broadcast",
        acknowledged=False,
        delivered=False,
        created_at=message.created_at,
    )


@router.post("/ack")
async def acknowledge_message(
    data: MessageAck,
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge receipt of a message."""
    result = await db.execute(
        select(Message).where(Message.id == UUID(data.message_id))
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.acknowledged = True
    message.acknowledged_at = datetime.now(timezone.utc)
    message.delivered = True
    message.delivered_at = datetime.now(timezone.utc)
    await db.flush()

    return {"status": "acknowledged", "message_id": data.message_id}

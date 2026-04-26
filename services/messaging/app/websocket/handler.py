# =============================================================================
# WebSocket Handler for Real-Time Messaging
# =============================================================================
from __future__ import annotations

import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real-time messaging."""

    def __init__(self):
        self.active: Dict[str, WebSocket] = {}
        self.channels: Dict[str, set] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)
        for ch in self.channels.values():
            ch.discard(user_id)

    async def send_to_user(self, user_id: str, data: dict):
        ws = self.active.get(user_id)
        if ws:
            await ws.send_json(data)

    async def broadcast(self, data: dict, exclude: str = None):
        for uid, ws in self.active.items():
            if uid != exclude:
                await ws.send_json(data)

    async def send_to_channel(self, channel_id: str, data: dict, exclude: str = None):
        members = self.channels.get(channel_id, set())
        for uid in members:
            if uid != exclude:
                await self.send_to_user(uid, data)

    def join_channel(self, user_id: str, channel_id: str):
        if channel_id not in self.channels:
            self.channels[channel_id] = set()
        self.channels[channel_id].add(user_id)


manager = ConnectionManager()


@router.websocket("/ws/messages")
async def websocket_endpoint(websocket: WebSocket):
    user_id = websocket.query_params.get("user_id", "anonymous")
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "join_channel":
                manager.join_channel(user_id, data["channel_id"])
                await websocket.send_json({"event": "joined", "channel_id": data["channel_id"]})

            elif action == "send_message":
                msg = {
                    "event": "new_message",
                    "sender_id": user_id,
                    "content": data.get("content", ""),
                    "priority": data.get("priority", "NORMAL"),
                    "channel_id": data.get("channel_id"),
                }
                if data.get("channel_id"):
                    await manager.send_to_channel(data["channel_id"], msg, exclude=user_id)
                elif data.get("recipient_id"):
                    await manager.send_to_user(data["recipient_id"], msg)

            elif action == "broadcast":
                msg = {
                    "event": "broadcast",
                    "sender_id": user_id,
                    "content": data.get("content", ""),
                    "priority": "CRITICAL",
                }
                await manager.broadcast(msg, exclude=user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)

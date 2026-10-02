"""
WebSocket Endpoint
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import manager
from app.core.logger import logger
import asyncio
import json

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/grid")
async def ws_grid(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "event": "connected",
            "data": {"message": "GridShield WebSocket connected"}
        })
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "ping":
                        await websocket.send_json({"event": "pong", "data": {}})
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                await websocket.send_json({"event": "heartbeat", "data": {}})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS error: {e}")
        await manager.disconnect(websocket)

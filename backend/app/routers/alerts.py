from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class AlertMessage(BaseModel):
    type: str
    title: str
    message: str
    severity: str = "info"
    metadata: Dict[str, Any] = {}


active_connections: List[WebSocket] = []


async def broadcast(message: Dict[str, Any]):
    living_connections: List[WebSocket] = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
            living_connections.append(connection)
        except Exception:
            # Drop dead connection
            pass
    active_connections.clear()
    active_connections.extend(living_connections)


@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({
            "type": "heartbeat",
            "message": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
        while True:
            # Keep connection alive; optionally receive pings from client
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


@router.post("/publish")
async def publish_alert(alert: AlertMessage):
    payload = {
        "type": alert.type,
        "title": alert.title,
        "message": alert.message,
        "severity": alert.severity,
        "metadata": alert.metadata,
        "timestamp": datetime.utcnow().isoformat()
    }
    await broadcast(payload)
    return {"delivered": len(active_connections)}




from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db, redis_client
from app.models import CodeFile, collaborators_table
from app.middleware.dependencies import get_current_user
import asyncio
import json

router = APIRouter(prefix="/ws", tags=["WebSockets"])

# Track active WebSocket connections per file
active_sessions = {}

@router.websocket("/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: int, db: AsyncSession = Depends(get_db)):
    """WebSocket connection for real-time collaborative editing."""
    await websocket.accept()
    
    query_params = websocket.scope.get("query_string", b"").decode()
    token = next((param.split("=")[1] for param in query_params.split("&") if param.startswith("token=")), None)
    
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return
    
    user = get_current_user(token)
    if not user:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return
    
    # Validate file access
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    
    if not file:
        await websocket.close(code=1003, reason="File not found")
        return
    
    is_owner = user["sub"] == file.owner_id
    is_collaborator = await db.execute(select(collaborators_table).where(
        (collaborators_table.c.user_id == user["sub"]) & (collaborators_table.c.file_id == file_id)
    ))
    
    if not is_owner and not is_collaborator.scalar():
        await websocket.close(code=1008, reason="Insufficient permissions")
        return
    
    if file_id not in active_sessions:
        active_sessions[file_id] = []
    active_sessions[file_id].append(websocket)
    
    async def listen_to_redis():
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"file_{file_id}")
        for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_json({"data": message["data"]})
    
    asyncio.create_task(listen_to_redis())
    
    try:
        while True:
            data = await websocket.receive_text()
            redis_client.publish(f"file_{file_id}", data)
    except WebSocketDisconnect:
        active_sessions[file_id].remove(websocket)
        await websocket.close(code=1000, reason="User disconnected")

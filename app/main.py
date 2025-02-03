from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict

app = FastAPI()

# Track connected users and their cursors
active_users: Dict[str, WebSocket] = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    Handles WebSocket connections for real-time collaboration.
    """
    await websocket.accept()
    active_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast changes to all users except sender
            for uid, connection in active_users.items():
                if uid != user_id:
                    await connection.send_json({"user": user_id, "data": data})
    except WebSocketDisconnect:
        del active_users[user_id]
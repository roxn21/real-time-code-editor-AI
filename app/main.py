from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# Active connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for real-time collaboration.
    """
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast message to all connected clients
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
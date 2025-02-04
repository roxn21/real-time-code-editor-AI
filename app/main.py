from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from app.auth.auth_service import create_jwt_token, verify_password, hash_password, decode_jwt_token  

app = FastAPI()

# Track connected users and their cursors
active_users: Dict[str, WebSocket] = {}

# Fake user database (for now)
fake_users_db = {
    "user1": {"password": hash_password("password123")}
}

class LoginInput(BaseModel):
    username: str
    password: str

@app.get("/health")
async def health_check():
    """Health check API to ensure FastAPI is running"""
    return {"status": "ok"}

@app.post("/login/")
async def login(user_data: LoginInput):
    """
    Login API to generate JWT token for authentication.
    """
    user = fake_users_db.get(user_data.username)
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = create_jwt_token(user_data.username)
    return {"access_token": token}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str = Query(...)):
    """
    Secure WebSocket connection using JWT authentication.
    """
    decoded_token = decode_jwt_token(token)
    if not decoded_token:
        await websocket.close()
        return

    await websocket.accept()
    active_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            # Broadcasting changes to all users except sender
            for uid, connection in active_users.items():
                if uid != user_id:
                    await connection.send_json({"user": user_id, "data": data})
    except WebSocketDisconnect:
        del active_users[user_id]
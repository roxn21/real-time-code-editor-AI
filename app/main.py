from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, redis_client
from app.models import User, CodeFile, EditingSession, collaborators_table
from app.schemas import UserCreate, UserOut, FileCreate, FileOut
from app.auth.auth_service import create_jwt_token, verify_password, hash_password, decode_jwt_token
from app.middleware.rbac import require_role, get_current_user
import asyncio
import json
from app.redis_client import redis_client

app = FastAPI(title="Real-Time Code Editor API", description="FastAPI backend for collaborative code editing with AI-powered debugging.", version="1.0")

# Track active WebSocket sessions per file
active_sessions: Dict[int, List[WebSocket]] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class LoginInput(BaseModel):
    username: str
    password: str

@app.get("/health", summary="Health Check", response_description="Service Health Status")
async def health_check():
    """Health check API to ensure FastAPI is running"""
    return {"status": "ok"}

@app.post("/login/", summary="User Login", response_description="Access Token")
async def login(user_data: LoginInput, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token"""
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = create_jwt_token(user.id, user.role)
    return {"access_token": token}

@app.post("/register/", response_model=UserOut, summary="User Registration", response_description="Registered User")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and store their credentials"""
    async with db.begin():
        result = await db.execute(select(User).where(User.username == user.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        new_user = User(
            username=user.username,
            hashed_password=hash_password(user.password),
            role=user.role
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    return new_user

@app.get("/files/", response_model=list[FileOut], summary="List Code Files", response_description="List of code files")
async def list_files(db: AsyncSession = Depends(get_db)):
    """Retrieve a list of all available code files"""
    result = await db.execute(select(CodeFile))
    files = result.scalars().all()

    if not files:
        raise HTTPException(status_code=404, detail="No files found")
    
    return files

@app.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: int, db: AsyncSession = Depends(get_db)):
    """WebSocket connection for real-time collaborative editing"""
    await websocket.accept()
    
    query_params = websocket.scope.get("query_string", b"").decode()
    token = next((param.split("=")[1] for param in query_params.split("&") if param.startswith("token=")), None)
    
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return
    
    user = decode_jwt_token(token)
    if not user:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return

    # Check file and permissions
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

class CodeRequest(BaseModel):
    code: str

@app.post("/ai-debug/", summary="AI Code Debugging", response_description="AI Suggestions")
async def ai_debug_code(request: CodeRequest):
    """Analyze code and return AI-generated debugging suggestions"""
    cached_result = redis_client.get(request.code)
    
    if cached_result:
        return json.loads(cached_result)
    
    ai_response = get_ai_suggestions(request.code)
    redis_client.setex(request.code, 3600, json.dumps(ai_response))
    return ai_response

def get_ai_suggestions(code: str):
    """Mock AI function to return debugging suggestions"""
    return {"suggestion": "Fix issue here!"}
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

app = FastAPI()

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

@app.get("/health")
async def health_check():
    """Health check API to ensure FastAPI is running"""
    return {"status": "ok"}

@app.post("/login/")
async def login(user_data: LoginInput, db: AsyncSession = Depends(get_db)):
    """ Login API to generate JWT token for authentication. """
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = create_jwt_token(user.id, user.role)
    return {"access_token": token}

@app.post("/register/", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """ Register a new user. """
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

@app.post("/create-file/", response_model=FileOut)
async def create_file(file_data: FileCreate, user: dict = Depends(require_role("owner")), db: AsyncSession = Depends(get_db)):
    """ Only owners can create new code files. """
    result = await db.execute(select(CodeFile).where(CodeFile.filename == file_data.filename))
    existing_file = result.scalars().first()
    if existing_file:
        raise HTTPException(status_code=400, detail="Filename already exists")

    new_file = CodeFile(filename=file_data.filename, owner_id=int(user["sub"]))
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    return new_file

@app.get("/files/", response_model=list[FileOut])
async def list_files(db: AsyncSession = Depends(get_db)):
    """ Get a list of all available code files. """
    result = await db.execute(select(CodeFile))
    files = result.scalars().all()

    if not files:
        raise HTTPException(status_code=404, detail="No files found")

    return files

@app.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: int, db: AsyncSession = Depends(get_db)):
    """ Secure WebSocket connection using JWT authentication & Redis Pub/Sub """
    
    # Accept WebSocket connection
    await websocket.accept()

    # Extract JWT token from query parameters
    query_params = websocket.scope.get("query_string", b"").decode()
    token = next((param.split("=")[1] for param in query_params.split("&") if param.startswith("token=")), None)

    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return

    # Decode JWT token
    user = decode_jwt_token(token)
    if not user:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return

    # Check if file exists
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    if not file:
        await websocket.close(code=1003, reason="File not found")
        return

    # Check if user is owner or collaborator
    is_owner = user["sub"] == file.owner_id
    is_collaborator = await db.execute(select(collaborators_table).where(
        (collaborators_table.c.user_id == user["sub"]) & (collaborators_table.c.file_id == file_id)
    ))

    if not is_owner and not is_collaborator.scalar():
        await websocket.close(code=1008, reason="Insufficient permissions")
        return

    # Track active sessions
    if file_id not in active_sessions:
        active_sessions[file_id] = []
    active_sessions[file_id].append(websocket)

    # Redis Pub/Sub Listener
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
            redis_client.publish(f"file_{file_id}", data)  # Cache message in Redis
    except WebSocketDisconnect:
        active_sessions[file_id].remove(websocket)
        await websocket.close(code=1000, reason="User disconnected")

@app.post("/files/{file_id}/add-collaborator/{collab_id}")
async def add_collaborator(file_id: int, collab_id: int, user: dict = Depends(require_role("owner")), db: AsyncSession = Depends(get_db)):
    """ Allows file owners to assign collaborators. """
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if user["sub"] != file.owner_id:
        raise HTTPException(status_code=403, detail="Only the file owner can add collaborators")

    await db.execute(collaborators_table.insert().values(user_id=collab_id, file_id=file_id))
    await db.commit()

    return {"message": f"User {collab_id} added as collaborator to file {file_id}"}

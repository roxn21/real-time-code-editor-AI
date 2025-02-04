from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, CodeFile
from app.schemas import UserCreate, UserOut, FileCreate, FileOut
from app.auth.auth_service import create_jwt_token, verify_password, hash_password, decode_jwt_token
from app.middleware.rbac import require_role
import logging

app = FastAPI()

# Track connected users and their cursors
active_users: Dict[str, WebSocket] = {}

class LoginInput(BaseModel):
    username: str
    password: str

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check API to ensure FastAPI is running"""
    return {"status": "ok"}

@app.post("/login/")
async def login(user_data: LoginInput, db: AsyncSession = Depends(get_db)):
    """
    Login API to generate JWT token for authentication.
    """
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Ensure user ID is passed to JWT function
    token = create_jwt_token(user.id, user.role)  
    return {"access_token": token}

@app.post("/register/", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if the username already exists
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
    """
    Only owners can create new code files.
    """
    # Check if filename already exists
    result = await db.execute(select(CodeFile).where(CodeFile.filename == file_data.filename))
    existing_file = result.scalars().first()
    if existing_file:
        raise HTTPException(status_code=400, detail="Filename already exists")

    # Create new file
    new_file = CodeFile(filename=file_data.filename, owner_id=user["sub"])
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    return new_file

@app.get("/files/", response_model=List[FileOut])
async def list_files(db: AsyncSession = Depends(get_db)):
    """
    Get a list of all available code files.
    """
    result = await db.execute(select(CodeFile))
    print(result.scalars().all())  # Debugging line
    return result.scalars().all()

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


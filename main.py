from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from celery.result import AsyncResult
from app.database import get_db, redis_client
from app.auth.auth_service import create_jwt_token, verify_password, hash_password
from app.celery_worker import analyze_code_task, celery_app
from app.services.ai_service import AIService
from app.models import User
from app.routes import files, collaboration
from app import websockets

app = FastAPI(title="Real-Time Code Editor API", description="FastAPI backend for collaborative code editing with AI-powered debugging.", version="1.0")

# Include Routers
app.include_router(files.router)
app.include_router(collaboration.router)
app.include_router(websockets.router)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", summary="Health Check", response_description="Service Health Status")
async def health_check():
    return {"status": "ok"}

# Login Endpoint
@app.post("/login/", summary="User Login", response_description="Access Token")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = create_jwt_token(user.id, user.role)
    return {"access_token": token}

# User Registration Endpoint
@app.post("/register/", summary="User Registration", response_description="Registered User")
async def register_user(username: str, password: str, role: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=username, hashed_password=hash_password(password), role=role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# AI Debugging Endpoint
@app.post("/ai-debug/", summary="AI Code Debugging", response_description="AI Suggestions")
async def ai_debug_code(code: str):
    ai_service = AIService()
    return ai_service.analyze_code(code)

# Asynchronous Code Analysis Endpoint
@app.post("/analyze/", summary="AI Code Analysis", response_description="Task ID")
async def analyze_code_api(code: str, background_tasks: BackgroundTasks):
    task = analyze_code_task.apply_async(args=[code])
    return {"task_id": task.id, "message": "Analysis started, check results later."}

# Task Status Endpoint
@app.get("/task-status/{task_id}", summary="Task Status", response_description="Task Status")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "status": task_result.state, "result": task_result.result if task_result.state == "SUCCESS" else None}
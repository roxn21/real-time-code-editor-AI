from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config
from fastapi import HTTPException
import redis

# Load Redis configuration from environment variables
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379)

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Database URL (Defaults to SQLite for development)
DATABASE_URL = config("DATABASE_URL", default="sqlite+aiosqlite:///./test.db")

# Create async engine (Fixes SQLite threading issue)
engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"timeout": 30, "check_same_thread": False})

# Define Base for models
Base = declarative_base()

# Create async session maker
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependency for FastAPI endpoints
async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
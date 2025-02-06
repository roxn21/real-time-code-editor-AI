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

# Use an environment variable for the database URL; defaulting to SQLite for simplicity.
DATABASE_URL = config("DATABASE_URL", default="sqlite+aiosqlite:///./test.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"timeout": 30})

# Define Base (Fix for ImportError in models.py)
Base = declarative_base()

# Create session maker for async sessions
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Dependency for FastAPI endpoints
async def get_db():
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
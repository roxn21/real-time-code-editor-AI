from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config

# Use an environment variable for the database URL; defaulting to SQLite for simplicity.
DATABASE_URL = config("DATABASE_URL", default="sqlite+aiosqlite:///./test.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Define Base (Fix for ImportError in models.py)
Base = declarative_base()

# Create session maker for async sessions
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Dependency for FastAPI endpoints
async def get_db():
    async with async_session() as session:
        yield session

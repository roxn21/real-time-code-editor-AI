import asyncio
from app.database import engine
from app.models import Base, collaborators_table 
from sqlalchemy.ext.asyncio import AsyncSession

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(lambda conn: collaborators_table.create(conn, checkfirst=True))  # Ensuring collaborators table exists

if __name__ == "__main__":
    asyncio.run(init_models())

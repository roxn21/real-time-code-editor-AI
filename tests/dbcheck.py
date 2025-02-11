import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text  # Import text()

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
async def test_connection():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:  
        result = await conn.execute(text("SELECT 1"))  
        rows = result.fetchall()  # Fetch results
        print(rows)  # Should print [(1,)]

asyncio.run(test_connection())

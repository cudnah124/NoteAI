"""Reset database schema"""
import asyncio
from app.core.database import Base, engine
from app import models  # Import all models


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database reset complete")


if __name__ == "__main__":
    asyncio.run(reset_db())

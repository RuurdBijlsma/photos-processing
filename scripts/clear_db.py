import asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.app_config import app_config

# Example async database URL
DATABASE_URL = app_config.connection_string


async def clear_database_with_async_sqlalchemy(database_url: str):
    """
    Drops all tables and associated objects (like sequences)
        from the database asynchronously.
    """
    # Create the async engine
    engine: AsyncEngine = create_async_engine(database_url, echo=True)

    # Use a connection to reflect and drop all tables
    async with engine.begin() as conn:
        metadata = MetaData()
        await conn.run_sync(metadata.reflect)  # Reflect tables
        await conn.run_sync(metadata.drop_all)  # Drop all tables
        print("All tables and related database objects dropped.")

    # Dispose the engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(clear_database_with_async_sqlalchemy(DATABASE_URL))

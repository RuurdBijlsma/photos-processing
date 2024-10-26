from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession


async def check_health(session: AsyncSession):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database connection error")

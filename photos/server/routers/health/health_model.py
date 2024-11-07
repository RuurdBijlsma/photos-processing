from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession


class HealthStatus(BaseModel):
    status: str


async def check_health(session: AsyncSession) -> HealthStatus:
    try:
        await session.execute(text("SELECT 1"))
        return HealthStatus(status="ok")
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database connection error")

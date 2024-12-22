from fastapi import APIRouter

from app.data.database.database import SessionDep
from app.routers.health.health_model import HealthStatus, check_health

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("")
async def health_check(db: SessionDep) -> HealthStatus:
    return await check_health(db)

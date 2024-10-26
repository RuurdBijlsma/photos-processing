from fastapi import APIRouter

from photos.data.database.database import SessionDep
from photos.server.routers.health.health_model import check_health

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("")
async def health_check(db: SessionDep) -> dict[str, str]:
    return await check_health(db)

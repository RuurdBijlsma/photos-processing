from collections.abc import Sequence
from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from app.data.database.database import SessionDep
from app.data.image_models import ImageModel
from app.data.interfaces.response_types import GridImageData
from app.routers.auth.auth_model import UserDep
from app.routers.images.images_model import scroll_down, scroll_up, at_date

images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.get("/at-date", response_model=list[GridImageData])
async def get_at_date(
    _: UserDep,
    session: SessionDep,
    lower_date: datetime = Query(default_factory=lambda: datetime(1970, 1, 1, 1, 1, 1)),
    date: datetime = Query(default_factory=lambda: datetime.now()),
    upper_date: datetime = Query(
        default_factory=lambda: datetime.now() + timedelta(days=1)
    ),
    limit: int = Query(default=100, ge=1, le=200),
) -> Sequence[ImageModel]:
    return await at_date(session, lower_date, date, upper_date, limit)


@images_router.get("/scroll-up", response_model=list[GridImageData])
async def get_scroll_up(
    _: UserDep,
    session: SessionDep,
    lower_date: datetime,
    upper_date: datetime = Query(
        default_factory=lambda: datetime.now() + timedelta(days=1)
    ),
    limit: int = Query(default=100, ge=1, le=200),
) -> Sequence[ImageModel]:
    """give newer photos. upper_date is next cached date in frontend."""
    return await scroll_up(session, lower_date, upper_date, limit)


@images_router.get("/scroll-down", response_model=list[GridImageData])
async def get_scroll_down(
    _: UserDep,
    session: SessionDep,
    upper_date: datetime,
    lower_date: datetime = Query(default_factory=lambda: datetime(1970, 1, 1, 1, 1, 1)),
    limit: int = Query(default=100, ge=1, le=200),
) -> Sequence[ImageModel]:
    """give older photos. lower_date is next cached date in frontend."""
    return await scroll_down(session, lower_date, upper_date, limit)

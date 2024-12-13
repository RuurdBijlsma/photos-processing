from collections.abc import Sequence
from datetime import datetime

from fastapi import APIRouter, Query

from app.data.database.database import SessionDep
from app.data.image_models import ImageModel
from app.data.interfaces.response_types import GridImageData
from app.routers.auth.auth_model import UserDep
from app.routers.images.images_model import get_month_photos

images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.get("/", response_model=list[GridImageData])
async def get_at_date(
    _: UserDep,
    session: SessionDep,
    year: int = Query(default_factory=lambda: datetime.now().year),
    month: int = Query(default_factory=lambda: datetime.now().month),
) -> Sequence[ImageModel]:
    return await get_month_photos(session, year, month)


from collections.abc import Sequence
from datetime import date, timedelta

from fastapi import APIRouter, Query

from data.interfaces.image_info_types import GridImageInfo
from photos.data.database.database import SessionDep
from photos.data.models.image_models import ImageModel
from photos.server.routers.auth.auth_model import UserDep
from photos.server.routers.images.images_model import list_images

images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.get("/list", response_model=list[GridImageInfo])
async def get_images_by_date(
    _: UserDep,
    session: SessionDep,
    from_date: date,
    to_date: date = Query(default_factory=lambda: date.today() + timedelta(weeks=100)),
) -> Sequence[ImageModel]:
    return await list_images(session, from_date, to_date)

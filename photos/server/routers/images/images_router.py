from collections.abc import Sequence

from fastapi import Query, APIRouter

from photos.data.database.database import SessionDep
from photos.data.interfaces.media_info_types import ThumbImageInfo
from photos.data.models.media_model import ImageModel
from photos.server.routers.auth.auth_model import UserDep
from photos.server.routers.images.images_model import list_images

images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.get("", response_model=list[ThumbImageInfo])
async def get_images(
    _: UserDep,
    session: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
) -> Sequence[ImageModel]:
    return await list_images(session, page, limit)

import logging
from collections.abc import Sequence

from fastapi import HTTPException, Query, APIRouter
from sqlalchemy import select

from photos.database.database import SessionDep
from photos.database.models import ImageModel
from photos.interfaces import ExifImageInfo, ThumbImageInfo

router = APIRouter(prefix="/images")


@router.post("", response_model=ExifImageInfo)
def post_image(
    image_info: ExifImageInfo, session: SessionDep
) -> ImageModel:
    logging.info(image_info)
    image_model = ImageModel(**image_info.dict())
    session.add(image_model)
    session.commit()
    session.refresh(image_model)
    return image_model


@router.get("", response_model=list[ThumbImageInfo])
def get_images(
    session: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
) -> Sequence[ImageModel]:
    offset = (page - 1) * limit
    images = (
        session.execute(select(ImageModel).offset(offset).limit(limit)).scalars().all()
    )

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images

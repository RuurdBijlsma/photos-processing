import logging
from collections.abc import Sequence

from fastapi import Depends, HTTPException, Query, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from photos.config.app_config import app_config
from photos.database.database import get_session
from photos.database.models import ImageModel
from photos.interfaces import ImageInfo, ImageExistsRequest

router = APIRouter(prefix="/images")


@router.post("", response_model=ImageInfo)
def post_image(
    image_info: ImageInfo, session: Session = Depends(get_session)
) -> ImageModel:
    logging.info(image_info)
    image_model = ImageModel(**image_info.dict())
    session.add(image_model)
    session.commit()
    session.refresh(image_model)
    return image_model


@router.get("", response_model=list[ImageInfo])
def get_images(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session),
) -> Sequence[ImageModel]:
    offset = (page - 1) * limit
    images = (
        session.execute(select(ImageModel).offset(offset).limit(limit)).scalars().all()
    )

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images


@router.post("/exists")
def image_exists(
    image_request: ImageExistsRequest, session: Session = Depends(get_session)
) -> bool:
    image_model = (
        session.query(ImageModel).filter_by(relative_path=image_request.path).first()
    )
    if image_model is None:
        return False

    assert image_model.id is not None
    # Check for each resolution
    for size in app_config.thumbnail_sizes:
        file_path = app_config.thumbnails_dir / image_model.id / f"{size}p.webp"
        if not file_path.exists():
            return False

    return True

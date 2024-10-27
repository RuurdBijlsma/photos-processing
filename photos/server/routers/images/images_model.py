from collections.abc import Sequence
from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from photos.data.models.image_models import ImageModel


async def list_images(
    session: AsyncSession,
    from_date: date,
    to_date: date
) -> Sequence[ImageModel]:
    images = (await session.execute(
        select(ImageModel)
        .options(selectinload(ImageModel.location))
        .where(ImageModel.datetime_local.between(from_date, to_date))
        .order_by(ImageModel.datetime_local.desc())
    )).scalars().all()

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images

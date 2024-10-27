from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from photos.data.models.image_models import ImageModel


async def list_images(session: AsyncSession, page: int, limit: int) -> Sequence[ImageModel]:
    offset = (page - 1) * limit
    images = (await session.execute(
        select(ImageModel).offset(offset).limit(limit)
    )).scalars().all()

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images

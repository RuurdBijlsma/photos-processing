import asyncio
from collections.abc import Sequence
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from photos.data.models.image_models import ImageModel


async def scroll_helper(
    session: AsyncSession,
    lower_date: datetime,
    upper_date: datetime,
    statement: Select[tuple[ImageModel]],
) -> Sequence[ImageModel]:
    if lower_date > upper_date:
        raise HTTPException(status_code=422, detail="Incorrect date bounds")

    images = (await session.execute(statement)).scalars().all()

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images


async def scroll_up(
    session: AsyncSession,
    lower_date: datetime,
    upper_date: datetime,
    limit: int,
) -> Sequence[ImageModel]:
    subquery = (
        (
            select(ImageModel)
            .where(
                lower_date < ImageModel.datetime_local,
                ImageModel.datetime_local < upper_date,
            )
            .order_by(ImageModel.datetime_local.asc())
            .limit(limit)
        )
        .subquery()
        .alias("subquery")
    )
    return await scroll_helper(
        session,
        lower_date,
        upper_date,
        (
            select(ImageModel)
            .options(selectinload(ImageModel.location))
            .join(subquery, ImageModel.id == subquery.c.id)
            .order_by(ImageModel.datetime_local.desc())
        ),
    )


async def scroll_down(
    session: AsyncSession,
    lower_date: datetime,
    upper_date: datetime,
    limit: int,
) -> Sequence[ImageModel]:
    return await scroll_helper(
        session,
        lower_date,
        upper_date,
        select(ImageModel)
        .options(selectinload(ImageModel.location))
        .where(
            lower_date < ImageModel.datetime_local,
            ImageModel.datetime_local < upper_date,
        )
        .order_by(ImageModel.datetime_local.desc())
        .limit(limit),
    )


async def at_date(
    session: AsyncSession,
    lower_date: datetime,
    date: datetime,
    upper_date: datetime,
    limit: int,
) -> Sequence[ImageModel]:
    if not (lower_date < date < upper_date):
        raise HTTPException(status_code=422, detail="Date not between given ranges")
    up_images, down_images = await asyncio.gather(
        scroll_up(session, date, upper_date, limit // 2),
        scroll_down(session, lower_date, date, limit - limit // 2),
    )
    images = list(up_images) + list(down_images)

    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    return images

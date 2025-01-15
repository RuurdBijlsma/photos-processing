import random
from collections.abc import Sequence
from datetime import datetime

from async_lru import alru_cache
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.database.database import get_session
from app.data.image_models import ImageModel


@alru_cache
async def get_rows_count() -> int:
    async with get_session() as session:
        return (await session.execute(select(func.count(ImageModel.id)))).scalar_one()


async def random_db_image(session: AsyncSession) -> str:
    # TODO: sometimes update get_row_count result (lru_cache)
    random_offset = random.randint(0, await get_rows_count() - 1)
    image_hash = (
        await session.execute(
            select(ImageModel.hash).offset(random_offset).limit(1),
        )
    ).scalar_one_or_none()
    return str(image_hash)


async def get_month_images(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime | None,
) -> Sequence[ImageModel]:
    if end_date is None:
        query = (
            select(ImageModel)
            .options(selectinload(ImageModel.location))
            .where(ImageModel.datetime_local >= start_date)
            .order_by(ImageModel.datetime_utc.desc())
        )
    else:
        query = (
            select(ImageModel)
            .options(selectinload(ImageModel.location))
            .where(ImageModel.datetime_local >= start_date)
            .where(ImageModel.datetime_local < end_date)
            .order_by(ImageModel.datetime_utc.desc())
        )

    return (await session.execute(query)).scalars().all()

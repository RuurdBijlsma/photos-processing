from collections.abc import Sequence

from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.image_models import ImageModel


async def get_month_photos(
    session: AsyncSession,
    year:int,
    month:int
) -> Sequence[ImageModel]:
    return (await session.execute(
            select(ImageModel)
            .where(extract('year', ImageModel.datetime_local) == year)
            .where(extract('month', ImageModel.datetime_local) == month)
            .order_by(ImageModel.datetime_local.asc())
    )).scalars().all()



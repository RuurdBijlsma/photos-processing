from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.image_models import ImageModel


async def get_month_photos(
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

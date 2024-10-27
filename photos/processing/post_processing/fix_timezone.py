import pytz
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from timezonefinder import TimezoneFinder
from tqdm import tqdm

from photos.data.models.image_models import ImageModel, UserModel

tf = TimezoneFinder()


async def fix_image_timezone(
    image: ImageModel, user_id: int, session: AsyncSession
) -> None | tuple[float, float]:
    image_with_tz = (await session.execute(
        select(ImageModel)
        .where(ImageModel.latitude.isnot(None))
        .where(ImageModel.longitude.isnot(None))
        .filter_by(user_id=user_id)
        .order_by(
            func.abs(
                func.extract("epoch", ImageModel.datetime_local)
                - func.extract("epoch", image.datetime_local)  # type: ignore
            )
        )
    )).scalar()
    if image_with_tz is None or not (image_with_tz.latitude and image_with_tz.longitude):
        return None
    return float(image_with_tz.latitude), float(image_with_tz.longitude)


async def fill_timezone_gaps(session: AsyncSession, user_id: int) -> None:
    try:
        images = (await session.execute(
            select(ImageModel).where(ImageModel.timezone_name.is_(None))
        )).scalars().all()
        closest_image_coordinates: list[tuple[float, float] | None] = []
        for image in tqdm(images, desc="Finding image timezones", unit="image"):
            closest_image_coordinates.append(await fix_image_timezone(image, user_id, session))
        for image, coordinate in tqdm(
            list(zip(images, closest_image_coordinates)),
            desc="Fixing timezones",
            unit="image",
        ):
            if coordinate is None:
                continue
            latitude, longitude = coordinate
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if timezone_str is None:
                continue
            local_tz = pytz.timezone(timezone_str)
            assert image.datetime_local is not None
            local_dt = local_tz.localize(image.datetime_local)
            assert local_dt is not None
            image.datetime_utc = local_dt.astimezone(pytz.utc)
            image.timezone_name = timezone_str
            image.timezone_offset = local_dt.utcoffset()
        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"An exception occurred: {e}")

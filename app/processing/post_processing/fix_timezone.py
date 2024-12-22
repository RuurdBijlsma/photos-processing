import pytz
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from timezonefinder import TimezoneFinder
from tqdm import tqdm

from app.data.image_models import ImageModel

tf = TimezoneFinder()


async def find_proximate_coordinate(
    image: ImageModel, user_id: int, session: AsyncSession,
) -> None | tuple[float, float]:
    image_with_tz = (
        await session.execute(
            select(ImageModel)
            .where(ImageModel.latitude.isnot(None))
            .where(ImageModel.longitude.isnot(None))
            .filter_by(user_id=user_id)
            .order_by(
                func.abs(
                    func.extract("epoch", ImageModel.datetime_local)
                    - func.extract("epoch", image.datetime_local),
                ),
            ),
        )
    ).scalar()
    if image_with_tz is None or not (
        image_with_tz.latitude and image_with_tz.longitude
    ):
        return None
    return float(image_with_tz.latitude), float(image_with_tz.longitude)


async def fill_timezone_gaps(session: AsyncSession, user_id: int) -> None:
    no_tz_images = (await session.execute(
        select(ImageModel).where(ImageModel.timezone_name.is_(None)),
    )).scalars().all()
    closest_image_coordinates: list[tuple[float, float] | None] = [
        await find_proximate_coordinate(image, user_id, session)
        for image in tqdm(no_tz_images, desc="Finding image timezones", unit="image")
    ]
    for image, coordinate in tqdm(
        list(zip(no_tz_images, closest_image_coordinates, strict=False)),
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
        datetime_utc = local_dt.astimezone(pytz.utc)
        datetime_utc = datetime_utc.replace(tzinfo=None)
        image.datetime_utc = datetime_utc
        image.timezone_name = timezone_str
        image.timezone_offset = local_dt.utcoffset()
        print(f"Fixed image: {image.filename}, {datetime_utc}")
    await session.commit()
    # todo find out if try except is needed here and which exception is thrown, rollback if except happens

import pytz
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from timezonefinder import TimezoneFinder
from tqdm import tqdm

from photos.database.database import get_session_maker
from photos.database.models import ImageModel, UserModel

tf = TimezoneFinder()


def fix_image_timezone(
    image: ImageModel, user: UserModel, session: Session
) -> None | tuple[float, float]:
    stmt = (
        select(ImageModel)
        .where(ImageModel.latitude.isnot(None))
        .where(ImageModel.longitude.isnot(None))
        .where(ImageModel.user_id.__eq__(user.id))
        .order_by(
            func.abs(
                func.extract("epoch", ImageModel.datetime_local)
                - func.extract("epoch", image.datetime_local)  # type: ignore
            )
        )
        .limit(1)
    )

    # Execute the query
    result = session.execute(stmt).scalars().first()
    if result is None or not (result.latitude and result.longitude):
        return None
    return float(result.latitude), float(result.longitude)


def fill_timezone_gaps(user: UserModel) -> None:
    session = get_session_maker()()
    try:
        images = (
            session.execute(
                select(ImageModel).where(ImageModel.timezone_name.is_(None))
            )
            .scalars()
            .all()
        )
        closest_image_coordinates: list[tuple[float, float] | None] = []
        for image in tqdm(images, desc="Finding image timezones", unit="image"):
            closest_image_coordinates.append(fix_image_timezone(image, user, session))
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
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"An exception occurred: {e}")
    finally:
        session.close()

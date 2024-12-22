import re
from datetime import datetime, timedelta, timezone

import pytz

from app.data.interfaces.image_data import GpsData, ImageData, TimeData
from app.processing.pipeline.base_module import FileModule
from app.processing.post_processing.timezone_finder import timezone_finder


def get_local_datetime(image_info: GpsData) -> tuple[datetime, str]:
    def f1() -> tuple[datetime, str]:
        assert image_info.exif
        datetime_taken = datetime.strptime(  # noqa: DTZ007
            image_info.exif["DateTimeOriginal"],
            "%Y:%m:%d %H:%M:%S",
        )
        offset_time = image_info.exif["OffsetTimeOriginal"]
        hours, minutes = map(int, offset_time.split(":"))
        offset = timedelta(hours=hours, minutes=minutes)
        result = datetime_taken.replace(tzinfo=timezone(offset))
        return result, "OffsetTime"

    def f2() -> tuple[datetime, str]:
        assert image_info.longitude and image_info.latitude
        tz_name = timezone_finder.timezone_at(
            lng=image_info.longitude,
            lat=image_info.latitude,
        )
        assert tz_name is not None
        assert image_info.datetime_utc
        datetime_utc = image_info.datetime_utc.replace(tzinfo=pytz.utc)
        result = datetime_utc.astimezone(pytz.timezone(tz_name))
        return result, "GPS"

    def f3() -> tuple[datetime, str]:
        assert image_info.exif
        result = datetime.strptime(  # noqa: DTZ007
            image_info.exif["DateTimeOriginal"],
            "%Y:%m:%d %H:%M:%S",
        )
        return result, "DateTimeOriginal"

    def f4() -> tuple[datetime, str]:
        assert image_info.exif
        result = datetime.strptime(image_info.exif["CreateDate"], "%Y:%m:%d %H:%M:%S")  # noqa: DTZ007
        return result, "DateTimeOriginal"

    def f5() -> tuple[datetime, str]:
        # Use a regex to find the first 8 digits (YYYYMMDD) and the subsequent time (HHMMSS)
        match = re.search(r"(\d{8})(\d{6})", image_info.filename)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            return (
                datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S"),  # noqa: DTZ007
                "Filename",
            )
        raise ValueError(f"Could not parse {image_info.filename}")

    def f6() -> tuple[datetime, str]:
        assert image_info.file
        assert "FileModifyDate" in image_info.file
        result = datetime.strptime(
            image_info.file["FileModifyDate"],
            "%Y:%m:%d %H:%M:%S%z",
        )
        return result, "ModificationDate"

    for fn in [f1, f2, f3, f4, f5, f6]:
        try:
            return fn()
        except (KeyError, AssertionError, ValueError):
            pass
    raise ValueError(f"Could not parse datetime for {image_info.filename}!")


def get_timezone_info(
    image_info: GpsData,
    date: datetime,
) -> tuple[datetime | None, str | None, timedelta | None]:
    """Gets timezone name and offset from latitude, longitude, and date."""
    if not image_info.latitude or not image_info.longitude:
        return None, None, None

    timezone_name = timezone_finder.timezone_at(
        lat=image_info.latitude,
        lng=image_info.longitude,
    )
    if not timezone_name:
        return None, None, None

    tz_date = pytz.timezone(timezone_name).localize(date.replace(tzinfo=None))
    timezone_offset = tz_date.utcoffset()

    datetime_utc = image_info.datetime_utc
    if datetime_utc is None:
        datetime_utc = tz_date.astimezone(pytz.utc)

    return datetime_utc, timezone_name, timezone_offset


class TimeModule(FileModule):
    def process(self, data: ImageData) -> TimeData:
        assert isinstance(data, GpsData)
        datetime_taken, datetime_source = get_local_datetime(data)
        datetime_utc, timezone_name, timezone_offset = get_timezone_info(
            data,
            datetime_taken,
        )
        if datetime_utc is not None:
            datetime_utc = datetime_utc.replace(tzinfo=None)
        data.datetime_utc = datetime_utc
        datetime_taken = datetime_taken.replace(tzinfo=None)

        return TimeData(
            **data.model_dump(),
            datetime_local=datetime_taken,
            datetime_source=datetime_source,
            timezone_name=timezone_name,
            timezone_offset=timezone_offset,
        )

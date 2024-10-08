import re
from datetime import datetime, timedelta, timezone

import pytz
from timezonefinder import TimezoneFinder

from photos.config.app_config import app_config
from photos.interfaces import TimeImageInfo, GpsImageInfo

tf = TimezoneFinder()


def parse_filename_datetime(filename: str) -> datetime | None:
    # Use a regex to find the first 8 digits (YYYYMMDD) and the subsequent time (HHMMSS)
    match = re.search(r"(\d{8})(\d{6})", filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
        except ValueError:
            return None
    else:
        return None


def get_modern_datetime(image_info: GpsImageInfo) -> datetime | None:
    if (
        image_info.exif
        and "EXIF" in image_info.exif
        and "DateTimeOriginal" in image_info.exif["EXIF"]
        and "OffsetTimeOriginal" in image_info.exif["EXIF"]
    ):
        datetime_taken = datetime.strptime(
            image_info.exif["EXIF"]["DateTimeOriginal"],
            "%Y:%m:%d %H:%M:%S",
        )
        offset_time = image_info.exif["EXIF"]["OffsetTimeOriginal"]
        hours, minutes = map(int, offset_time.split(":"))
        offset = timedelta(hours=hours, minutes=minutes)
        return datetime_taken.replace(tzinfo=timezone(offset))
    return None


def get_gps_datetime(image_info: GpsImageInfo) -> datetime | None:
    if (
        image_info.datetime_utc
        and image_info.latitude is not None
        and image_info.longitude is not None
    ):
        tz = tf.timezone_at(lng=image_info.longitude, lat=image_info.latitude)
        assert tz is not None
        return image_info.datetime_utc.astimezone(pytz.timezone(tz))
    return None


def get_exif_datetime_original(image_info: GpsImageInfo) -> datetime | None:
    if (
        image_info.exif
        and "EXIF" in image_info.exif
        and "DateTimeOriginal" in image_info.exif["EXIF"]
    ):
        return datetime.strptime(
            image_info.exif["EXIF"]["DateTimeOriginal"],
            "%Y:%m:%d %H:%M:%S",
        )
    return None


def get_exif_image_datetime(image_info: GpsImageInfo) -> datetime | None:
    if (
        image_info.exif
        and "Image" in image_info.exif
        and "DateTime" in image_info.exif["Image"]
    ):
        return datetime.strptime(
            image_info.exif["Image"]["DateTime"],
            "%Y:%m:%d %H:%M:%S",
        )
    return None


def get_local_datetime(image_info: GpsImageInfo) -> tuple[datetime, str]:
    datetime_source: str | None = None
    datetime_taken: datetime | None = None
    filename_datetime = parse_filename_datetime(image_info.filename)
    # First try: Get from datetime+tz from exif fields if they exist
    try:
        datetime_taken = get_modern_datetime(image_info)
        datetime_source = "OffsetTimeOriginal"
    except ValueError:
        ...
    # Second try: Get datetime+tz from GPS time (utc) and gps coordinate for tz
    if datetime_taken is None:
        datetime_taken = get_gps_datetime(image_info)
        datetime_source = "GPS"
    # Third try, no tz information available, get from EXIF>DateTimeOriginal
    if datetime_taken is None:
        try:
            datetime_taken = get_exif_datetime_original(image_info)
            datetime_source = "DateTimeOriginal"
        except ValueError:
            ...
    # Fourth try, get from Image>DateTime
    if datetime_taken is None:
        datetime_taken = get_exif_image_datetime(image_info)
        datetime_source = "DateTime"
    # Fifth try: get it from filename
    if datetime_taken is None and filename_datetime:
        datetime_taken = filename_datetime
        datetime_source = "Filename"
    # Last try: Get it from file modification datetime
    if datetime_taken is None:
        file_path = app_config.photos_dir / image_info.relative_path
        creation_time = file_path.stat().st_mtime
        datetime_taken = datetime.fromtimestamp(creation_time)
        datetime_source = "ModificationDate"

    assert datetime_taken is not None
    assert datetime_source is not None
    return datetime_taken, datetime_source


def get_timezone_info(
    lat: float, lon: float, date: datetime
) -> tuple[str | None, timedelta | None]:
    """Gets timezone name and offset from latitude, longitude, and date."""

    timezone_str = tf.timezone_at(lat=lat, lng=lon)
    if not timezone_str:
        return None, None

    timezone_offset = (
        pytz.timezone(timezone_str).localize(date.replace(tzinfo=None)).utcoffset()
    )
    return timezone_str, timezone_offset


def get_time_taken(image_info: GpsImageInfo) -> TimeImageInfo:
    datetime_taken, datetime_source = get_local_datetime(image_info)
    # Fix cringe timezone (offset based) to one based on location
    if (
        datetime_taken.tzinfo is not None
        and isinstance(datetime_taken.tzinfo, timezone)
        and image_info.datetime_utc
        and image_info.latitude is not None
        and image_info.longitude is not None
    ):
        tz = tf.timezone_at(lng=image_info.longitude, lat=image_info.latitude)
        assert tz is not None
        datetime_taken = datetime_taken.replace(tzinfo=pytz.timezone(tz))

    timezone_name: str | None = None
    timezone_offset: timedelta | None = None
    if image_info.latitude is not None and image_info.longitude is not None:
        timezone_name, timezone_offset = get_timezone_info(
            image_info.latitude, image_info.longitude, datetime_taken
        )
    return TimeImageInfo(
        **image_info.model_dump(),
        datetime_local=datetime_taken,
        datetime_source=datetime_source,
        timezone_name=timezone_name,
        timezone_offset=timezone_offset,
    )

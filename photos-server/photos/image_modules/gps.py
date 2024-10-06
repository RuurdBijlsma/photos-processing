from datetime import datetime, UTC
from typing import Any

import reverse_geocode

from photos.interfaces import ExifImageInfo, GpsImageInfo, GeoLocation


def dms_to_decimal(degrees: float, minutes: float, seconds: float) -> float:
    """Convert degrees, minutes, seconds to decimal format."""
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def parse_exif_gps(
    exif_gps: dict[str | int, Any],
) -> dict[str, float | datetime | None]:
    # Parse latitude
    lat_dms = exif_gps.get(2)
    lat_ref = exif_gps.get(3, "N")  # Defaults to 'N' if not found
    if lat_dms:
        latitude = dms_to_decimal(
            lat_dms[0][0] / lat_dms[0][1],
            lat_dms[1][0] / lat_dms[1][1],
            lat_dms[2][0] / lat_dms[2][1],
        )
        if lat_ref == "S":  # Southern hemisphere should be negative
            latitude = -latitude
    else:
        latitude = None

    # Parse longitude
    lon_dms = exif_gps.get(4)
    lon_ref = exif_gps.get(5, "E")  # Defaults to 'E' if not found
    if lon_dms:
        longitude = dms_to_decimal(
            lon_dms[0][0] / lon_dms[0][1],
            lon_dms[1][0] / lon_dms[1][1],
            lon_dms[2][0] / lon_dms[2][1],
        )
        if lon_ref == "W":  # Western hemisphere should be negative
            longitude = -longitude
    else:
        longitude = None

    # Parse altitude
    altitude_data = exif_gps.get(6)
    if altitude_data:
        altitude = altitude_data[0] / altitude_data[1]
        if altitude_data[1] == 1:  # Below sea level
            altitude = -altitude
    else:
        altitude = None

    gps_datetime: datetime | None = None
    gps_date = exif_gps.get(29)
    gps_time_data = exif_gps.get(7)
    if gps_time_data and gps_date:
        hours = gps_time_data[0][0] / gps_time_data[0][1]
        minutes = gps_time_data[1][0] / gps_time_data[1][1]
        seconds = gps_time_data[2][0] / gps_time_data[2][1]
        gps_datetime = datetime.strptime(gps_date, "%Y:%m:%d")
        gps_datetime = gps_datetime.replace(
            hour=int(hours), minute=int(minutes), second=int(seconds), tzinfo=UTC
        )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "datetime": gps_datetime,
    }


def get_gps_image(image_info: ExifImageInfo) -> GpsImageInfo:
    if not image_info.exif or "GPS" not in image_info.exif:
        return GpsImageInfo(**image_info.model_dump())
    gps_data = parse_exif_gps(image_info.exif["GPS"])
    if (
        gps_data["latitude"] is None
        or gps_data["longitude"] is None
        or gps_data["datetime"] is None
        or gps_data["altitude"] is None
    ):
        return GpsImageInfo(**image_info.model_dump())
    assert isinstance(gps_data["latitude"], float)
    assert isinstance(gps_data["longitude"], float)
    assert isinstance(gps_data["altitude"], float)
    assert isinstance(gps_data["datetime"], datetime)
    coded = reverse_geocode.get((gps_data["latitude"], gps_data["longitude"]))
    return GpsImageInfo(
        **image_info.model_dump(),
        latitude=gps_data["latitude"],
        longitude=gps_data["longitude"],
        altitude=gps_data["altitude"],
        gps_datetime=gps_data["datetime"],
        location=GeoLocation(
            country=coded["country"],
            province=coded["state"],
            city=coded["city"],
            latitude=coded["latitude"],
            longitude=coded["longitude"],
        ),
    )

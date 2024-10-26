import logging
from datetime import datetime

import reverse_geocode

from photos.data.interfaces.location_types import GeoLocation
from photos.data.interfaces.media_info_types import ExifImageInfo, GpsImageInfo


def get_gps_image(image_info: ExifImageInfo) -> GpsImageInfo:
    if (
        not image_info.composite
        or "GPSLatitude" not in image_info.composite
        or "GPSLongitude" not in image_info.composite
    ):
        return GpsImageInfo(**image_info.model_dump())

    lat = image_info.composite["GPSLatitude"]
    lon = image_info.composite["GPSLongitude"]
    if not lat or not lon:
        return GpsImageInfo(**image_info.model_dump())

    alt = image_info.composite.get("GPSAltitude")
    gps_datetime: datetime | None = None
    if "GPSDateTime" in image_info.composite:
        for date_fmt in ["%Y:%m:%d %H:%M:%S.%fZ", "%Y:%m:%d %H:%M:%SZ"]:
            try:
                gps_datetime = datetime.strptime(
                    image_info.composite["GPSDateTime"], date_fmt
                )
                if gps_datetime is not None:
                    break
            except ValueError:
                pass

    coded = reverse_geocode.get((lat, lon))
    return GpsImageInfo(
        **image_info.model_dump(),
        latitude=lat,
        longitude=lon,
        altitude=alt,
        datetime_utc=gps_datetime,
        location=GeoLocation(
            country=coded["country"],
            province=coded.get("state"),
            city=coded["city"],
            latitude=coded["latitude"],
            longitude=coded["longitude"],
        ),
    )

from datetime import datetime, UTC
from typing import Any

import piexif
import reverse_geocode

from photos.interfaces import ExifImageInfo, GpsImageInfo, GeoLocation


def convert_to_degrees(value: list[list[int]]) -> float:
    """Converts the GPS coordinates stored in EXIF format to degrees in float."""
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1] / 60.0
    s = value[2][0] / value[2][1] / 3600.0
    return d + m + s


def parse_exif_gps(
    gps_info: dict[str, Any],
) -> tuple[float | None, float | None, float | None, datetime | None]:
    """Extracts GPS coordinates, altitude, and GPS datetime from EXIF data."""
    gps_latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
    gps_latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
    gps_longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)
    gps_longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)
    gps_altitude = gps_info.get(piexif.GPSIFD.GPSAltitude, None)
    gps_date_str = gps_info.get(piexif.GPSIFD.GPSDateStamp, None)
    gps_time_obj = gps_info.get(piexif.GPSIFD.GPSTimeStamp, None)

    if gps_latitude is None or gps_longitude is None:
        return None, None, None, None

    lat = convert_to_degrees(gps_latitude)
    if gps_latitude_ref and gps_latitude_ref != "N":
        lat = -lat

    lon = convert_to_degrees(gps_longitude)
    if gps_longitude_ref and gps_longitude_ref != "E":
        lon = -lon

    # Convert altitude if present
    alt = gps_altitude[0] / gps_altitude[1] if gps_altitude else 0

    try:
        # GPS DateTime format is "YYYY:MM:DD"
        gps_datetime = datetime.strptime(gps_date_str, "%Y:%m:%d")
        hours = gps_time_obj[0][0] / gps_time_obj[0][1]
        minutes = gps_time_obj[1][0] / gps_time_obj[1][1]
        seconds = gps_time_obj[2][0] / gps_time_obj[2][1]
        gps_datetime = gps_datetime.replace(
            hour=int(hours), minute=int(minutes), second=int(seconds), tzinfo=UTC
        )
    except ValueError:
        print(f"Failed to parse gps datetime, got '{gps_date_str}' as date-str")
        gps_datetime = None

    return lat, lon, alt, gps_datetime


def get_gps_image(image_info: ExifImageInfo) -> GpsImageInfo:
    if not image_info.exif or "GPS" not in image_info.exif:
        return GpsImageInfo(**image_info.model_dump())
    lat, lon, alt, gps_datetime = parse_exif_gps(image_info.exif["GPS"])
    if lat is None or lon is None or alt is None:
        return GpsImageInfo(**image_info.model_dump())
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

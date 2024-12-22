from datetime import datetime

import reverse_geocode

from app.data.interfaces.image_data import ExifData, GpsData, ImageData
from app.data.interfaces.location_types import GeoLocation
from app.processing.pipeline.base_module import FileModule


class GpsModule(FileModule):
    def process(self, data: ImageData) -> GpsData:
        assert isinstance(data, ExifData)
        if (
                not data.composite
                or "GPSLatitude" not in data.composite
                or "GPSLongitude" not in data.composite
        ):
            return GpsData(**data.model_dump())

        lat = data.composite["GPSLatitude"]
        lon = data.composite["GPSLongitude"]
        if not lat or not lon:
            return GpsData(**data.model_dump())

        alt = data.composite.get("GPSAltitude")
        gps_datetime: datetime | None = None
        if "GPSDateTime" in data.composite:
            for date_fmt in ["%Y:%m:%d %H:%M:%S.%fZ", "%Y:%m:%d %H:%M:%SZ"]:
                try:
                    gps_datetime = datetime.strptime(  # noqa: DTZ007
                        data.composite["GPSDateTime"], date_fmt,
                    )
                    if gps_datetime is not None:
                        break
                except ValueError:
                    pass

        coded = reverse_geocode.get((lat, lon))
        return GpsData(
            **data.model_dump(),
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

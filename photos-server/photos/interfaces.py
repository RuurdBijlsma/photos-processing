from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_serializer


class BaseImageInfo(BaseModel):
    id: str
    filename: str
    relative_path: Path
    hash: str

    @field_serializer("relative_path")
    def serialize_relative_path(self, relative_path: Path) -> str:
        return str(relative_path)


class ThumbImageInfo(BaseImageInfo):
    width: int
    height: int
    format: str


class ExifImageInfo(ThumbImageInfo):
    exif: dict[str, Any] | None


class GeoLocation(BaseModel):
    country: str
    province: str
    city: str
    latitude: float
    longitude: float


class GpsImageInfo(ExifImageInfo):
    latitude: float | None = None
    longitude: float | None = None
    altitude: float | None = None
    datetime_utc: datetime | None = None
    location: GeoLocation | None = None


class TimeImageInfo(GpsImageInfo):
    datetime_local: datetime
    datetime_source: str
    timezone_name: str | None
    timezone_offset: timedelta | None

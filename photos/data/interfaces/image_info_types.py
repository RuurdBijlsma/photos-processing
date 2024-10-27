from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import field_serializer, BaseModel

from photos.data.interfaces.location_types import GeoLocation


class BaseImageInfo(BaseModel):
    id: str
    filename: str
    relative_path: Path
    hash: str

    @field_serializer("relative_path")
    def serialize_relative_path(self, relative_path: Path) -> str:
        return relative_path.as_posix()


class DataUrlImageInfo(BaseImageInfo):
    data_url: str


class DominantColorImageInfo(DataUrlImageInfo):
    dominant_colors: list[str]


class ThumbImageInfo(DominantColorImageInfo):
    width: int
    height: int
    duration: float | None
    size_bytes: int
    format: str


class ExifImageInfo(ThumbImageInfo):
    exif_tool: dict[str, Any]
    file: dict[str, Any]
    composite: dict[str, Any]
    exif: dict[str, Any] | None
    xmp: dict[str, Any] | None
    jfif: dict[str, Any] | None
    icc_profile: dict[str, Any] | None
    gif: dict[str, Any] | None
    quicktime: dict[str, Any] | None
    matroska: dict[str, Any] | None


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

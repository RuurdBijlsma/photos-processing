from datetime import datetime

from app.data.interfaces.image_info_types import BaseImageInfo
from app.data.interfaces.location_types import GeoLocationSmall


class GridImageInfo(BaseImageInfo):
    """Image info representation for frontend."""

    width: int
    height: int
    duration: float | None
    format: str
    data_url: str
    datetime_local: datetime
    location: GeoLocationSmall | None

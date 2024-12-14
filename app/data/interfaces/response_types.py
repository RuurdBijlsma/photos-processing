from datetime import datetime

from pydantic import ConfigDict

from app.data.interfaces.image_data import ImageData
from app.data.interfaces.location_types import GeoLocationSmall


class GridImageData(ImageData):
    """Image info representation for frontend."""

    width: int
    height: int
    duration: float | None
    format: str
    data_url: str
    datetime_local: datetime
    location: GeoLocationSmall | None

    model_config = ConfigDict(from_attributes=True)

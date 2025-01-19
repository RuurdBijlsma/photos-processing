from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LocationResponse(BaseModel):
    country: str
    city: str
    province: str | None


class ImageResponse(BaseModel):
    """Image info representation for frontend."""

    id: str
    filename: str
    width: int
    height: int
    duration: float | None
    format: str
    data_url: str
    datetime_local: datetime
    location: LocationResponse | None

    model_config = ConfigDict(from_attributes=True)

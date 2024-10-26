from pydantic import BaseModel


class GeoLocation(BaseModel):
    country: str
    province: str | None
    city: str
    latitude: float
    longitude: float
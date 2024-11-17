from pydantic import BaseModel


class GeoLocationSmall(BaseModel):
    country: str
    city: str


class GeoLocation(GeoLocationSmall):
    province: str | None
    latitude: float
    longitude: float

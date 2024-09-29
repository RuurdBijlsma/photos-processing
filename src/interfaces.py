from uuid import UUID

from pydantic import BaseModel


# Pydantic model for response
class Thumbnail(BaseModel):
    width: int
    height: int
    size: int
    path: str


class ImageResponse(BaseModel):
    id: UUID
    filename: str
    path: str
    format: str
    width: int
    height: int
    thumbnails: list[Thumbnail]

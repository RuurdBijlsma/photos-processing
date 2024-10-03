from typing import Any

from pydantic import BaseModel


class ImageInfoResponse(BaseModel):
    id: str
    filename: str
    width: int
    height: int


class ImageInfo(BaseModel):
    id: str
    filename: str
    relative_path: str
    hash: str
    width: int
    height: int
    format: str
    exif: None | dict[str, Any]


class ImageExistsRequest(BaseModel):
    path: str

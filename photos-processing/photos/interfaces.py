from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_serializer


class ImageInfo(BaseModel):
    id: str
    filename: str
    relative_path: Path
    hash: str
    width: int
    height: int
    format: str
    exif: None | dict[str, Any]

    @field_serializer('relative_path')
    def serialize_relative_path(self, relative_path: Path, _info):
        return str(relative_path)

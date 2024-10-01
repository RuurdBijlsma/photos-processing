from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ImageInfo:
    id: str
    filename: str
    relative_path: Path
    hash: str
    width: int
    height: int
    format: str
    exif: None | dict[str, Any]

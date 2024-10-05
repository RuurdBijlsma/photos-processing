import os
import uuid
from pathlib import Path

from photos.interfaces import BaseImageInfo


def base_info(
    photos_dir: Path,
    image_path: Path,
    image_hash: str,
) -> BaseImageInfo:
    return BaseImageInfo(
        id=uuid.uuid4().hex,
        relative_path=image_path.relative_to(photos_dir),
        filename=os.path.basename(image_path),
        hash=image_hash,
    )

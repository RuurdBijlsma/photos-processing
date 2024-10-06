import hashlib
import os
import uuid
from pathlib import Path

from photos.interfaces import BaseImageInfo


def hash_image(image_path: Path, chunk_size: int = 65536) -> str:
    hasher = hashlib.sha256()

    with image_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def base_info(
    photos_dir: Path,
    image_path: Path,
) -> BaseImageInfo:
    return BaseImageInfo(
        id=uuid.uuid4().hex,
        relative_path=image_path.relative_to(photos_dir),
        filename=os.path.basename(image_path),
        hash=hash_image(image_path),
    )

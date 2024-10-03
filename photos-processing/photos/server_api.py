import os
from pathlib import Path

import httpx

from photos.config.app_config import app_config
from photos.interfaces import ImageInfo
from photos.utils import clean_object

server_url = os.environ.get("SERVER_API_URL", "http://localhost:9475")


def image_exists(image_path: Path) -> bool:
    relative_path = image_path.relative_to(app_config.photos_dir)
    response = httpx.post(
        f"{server_url}/images/exists",
        json={
            "path": str(relative_path),
        },
    )
    response.raise_for_status()
    exists = response.json()
    assert isinstance(exists, bool)
    return exists


def store_image(image_info: ImageInfo) -> None:
    model_dump = clean_object(image_info.model_dump())
    response = httpx.post(f"{server_url}/images", json=model_dump)
    response.raise_for_status()

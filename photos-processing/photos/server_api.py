import os
from dataclasses import asdict

import httpx

from photos.interfaces import ImageInfo

server_url = os.environ.get("SERVER_API_URL", "http://localhost:9475")


def store_image(image_info: ImageInfo) -> None:
    return
    response = httpx.post(f"{server_url}/store-image", json=asdict(image_info))
    response.raise_for_status()

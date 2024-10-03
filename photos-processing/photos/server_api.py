import os

import httpx

from photos.interfaces import ImageInfo
from photos.utils import clean_object

server_url = os.environ.get("SERVER_API_URL", "http://localhost:9475")


def store_image(image_info: ImageInfo) -> None:
    model_dump = clean_object(image_info.model_dump())
    url = f"{server_url}/images"
    response = httpx.post(url, json=model_dump)
    response.raise_for_status()

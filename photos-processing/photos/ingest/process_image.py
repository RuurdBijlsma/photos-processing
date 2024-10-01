import hashlib
from pathlib import Path

from photos.config.process_config import ProcessConfig
from photos.image_modules.base_info import base_info
from photos.image_modules.generate_thumbnails import generate_thumbnails
from photos.server_api import store_image


def image_needs_processing(image_path: Path, hash: str) -> bool:
    return True


def hash_image(image_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def process_image(
        photos_dir: Path,
        image_path: Path,
        process_config: ProcessConfig
) -> None:
    image_hash = hash_image(image_path)

    if not image_needs_processing(image_path, image_hash):
        return

    image_info = base_info(photos_dir, image_path, image_hash, process_config)
    generate_thumbnails(photos_dir, image_info, process_config)

    store_image(image_info)

import os
from pathlib import Path

from PIL import Image

from photos.config.process_config import ProcessConfig
from photos.interfaces import ImageInfo


def generate_thumbnails(photos_dir: Path, image_info: ImageInfo, process_config: ProcessConfig) -> None:
    folder = process_config.thumbnails_dir / image_info.id
    if not os.path.exists(folder):
        os.makedirs(folder)

    with Image.open(photos_dir / image_info.relative_path) as img:
        for size in process_config.thumbnail_sizes:
            img_copy = img.copy()
            img_copy.thumbnail((size / img.height * img.width, size))
            thumb_name = f"{size}p.webp"
            thumb_path = os.path.join(folder, thumb_name)
            img_copy.save(thumb_path, format="WEBP")

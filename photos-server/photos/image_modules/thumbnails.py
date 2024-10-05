import os

from PIL.ImageFile import ImageFile

from photos.config.process_config import process_config
from photos.interfaces import BaseImageInfo


def generate_thumbnails(img: ImageFile, image_info: BaseImageInfo) -> None:
    folder = process_config.thumbnails_dir / image_info.id
    if not os.path.exists(folder):
        os.makedirs(folder)

    for size in process_config.thumbnail_sizes:
        img_copy = img.copy()
        img_copy.thumbnail((size / img.height * img.width, size))
        thumb_name = f"{size}p.webp"
        thumb_path = os.path.join(folder, thumb_name)
        img_copy.save(thumb_path, format="WEBP")

import os

import ffmpeg
from PIL.ImageFile import ImageFile

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.interfaces import BaseImageInfo


def generate_pillow_thumbnail(img: ImageFile, height: int, thumb_path: str) -> None:
    img_copy = img.copy()
    img_copy.thumbnail((height / img.height * img.width, height))
    img_copy.save(thumb_path, format="WEBP")


def generate_ffmpeg_thumbnail(image_info: BaseImageInfo, height: int, thumb_path: str) -> None:
    input_file = app_config.photos_dir / image_info.relative_path
    (ffmpeg
     .input(input_file)
     .filter('scale', -1, height)
     .output(thumb_path)
     .run(quiet=True))


def generate_thumbnails(img: ImageFile, image_info: BaseImageInfo) -> None:
    folder = process_config.thumbnails_dir / image_info.id
    if not os.path.exists(folder):
        os.makedirs(folder)

    for height in process_config.thumbnail_sizes:
        thumb_name = f"{height}p.webp"
        thumb_path = os.path.join(folder, thumb_name)
        try:
            generate_ffmpeg_thumbnail(image_info, height, thumb_path)
        except OSError:
            print("FFMPEG FAILED!")
            generate_pillow_thumbnail(img, height, thumb_path)

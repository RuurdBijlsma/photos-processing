import os
import uuid
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import IFDRational

from photos.config.process_config import ProcessConfig
from photos.interfaces import ImageInfo


def base_info(
        photos_dir: Path,
        image_path: Path,
        image_hash: str,
        _: ProcessConfig,
) -> ImageInfo:
    # Open the original image
    with Image.open(image_path) as img:
        width, height = img.size
        raw_exif = img.getexif()

        # Convert EXIF data to a readable format
        exif_info = {}
        for tag, value in raw_exif.items():
            tag_name = TAGS.get(tag, tag)
            if isinstance(value, IFDRational):
                value = float(value)
            exif_info[tag_name] = value

        return ImageInfo(
            id=uuid.uuid4().hex,
            width=width,
            height=height,
            format=img.format,
            relative_path=image_path.relative_to(photos_dir),
            filename=os.path.basename(image_path),
            exif=exif_info,
            hash=image_hash
        )

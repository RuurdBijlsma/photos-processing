import logging
from pathlib import Path

from exiftool.exceptions import ExifToolExecuteError
from sqlalchemy.ext.asyncio import AsyncSession

from photos.data.database.db_utils import store_image
from photos.data.interfaces.image_info_types import ExifImageInfo
from photos.data.models.image_models import UserModel
from photos.processing.pipelines.base_info import base_info
from photos.processing.pipelines.add_dominant_color import add_dominant_color
from photos.processing.pipelines.add_exif import add_exif_info
from photos.processing.pipelines.add_gps import add_gps_info
from photos.processing.pipelines.add_data_url import add_data_url
from photos.processing.pipelines.generate_thumbnails import generate_thumbnails
from photos.processing.pipelines.add_time_taken import add_time_taken
from photos.processing.process_utils import readable_bytes


def print_processing_update(image_info: ExifImageInfo):
    print_str = (
        f"{image_info.filename}\t\t--\t\t"
        f"{readable_bytes(image_info.size_bytes)}, {image_info.width} x {image_info.height}"
    )
    if image_info.duration is not None:
        print_str += f", {image_info.duration:3.1f}s"
    print(print_str)


async def process_media(image_info: Path, user_id: int, session: AsyncSession) -> None:
    image_info = base_info(image_info)
    image_info = add_data_url(image_info)
    image_info = add_dominant_color(image_info)

    try:
        image_info = add_exif_info(image_info)
    except ExifToolExecuteError:
        print(f"Failed to process {image_info}")
        return None

    print_processing_update(image_info)
    await generate_thumbnails(image_info)

    image_info = add_gps_info(image_info)
    image_info = add_time_taken(image_info)

    await store_image(image_info, user_id, session)

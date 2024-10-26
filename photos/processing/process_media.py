import logging
from pathlib import Path

from exiftool.exceptions import ExifToolExecuteError
from sqlalchemy.ext.asyncio import AsyncSession

from photos.data.database.db_utils import store_image
from photos.data.interfaces.media_info_types import ExifImageInfo
from photos.data.models.media_model import UserModel
from photos.processing.pipelines.base_info import base_info
from photos.processing.pipelines.exif import get_exif
from photos.processing.pipelines.gps import get_gps_image
from photos.processing.pipelines.thumbnails import generate_thumbnails
from photos.processing.pipelines.time_taken import get_time_taken
from photos.processing.process_utils import readable_bytes


def print_processing_update(media_info: ExifImageInfo):
    print_str = (
        f"{media_info.filename}\t\t--\t\t"
        f"{readable_bytes(media_info.size_bytes)}, {media_info.width} x {media_info.height}"
    )
    if media_info.duration is not None:
        print_str += f", {media_info.duration:3.1f}s"
    print(print_str)


async def process_media(media_path: Path, user_id: int, session: AsyncSession) -> None:
    image_info = base_info(media_path)

    try:
        image_info = get_exif(image_info)
    except ExifToolExecuteError:
        print(f"Failed to process {image_info}")
        return None

    print_processing_update(image_info)
    await generate_thumbnails(image_info)

    image_info = get_gps_image(image_info)
    image_info = get_time_taken(image_info)

    await store_image(image_info, user_id, session)

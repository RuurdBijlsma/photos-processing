from pathlib import Path

from exiftool.exceptions import ExifToolExecuteError
from sqlalchemy.ext.asyncio import AsyncSession

from photos.data.database.db_utils import store_image
from photos.processing.pipelines.add_data_url import add_data_url
from photos.processing.pipelines.add_exif import add_exif_info
from photos.processing.pipelines.add_gps import add_gps_info
from photos.processing.pipelines.add_time_taken import add_time_taken
from photos.processing.pipelines.base_info import base_info
from photos.processing.pipelines.generate_thumbnails import generate_thumbnails
from photos.processing.process_utils import readable_bytes
from processing.pipelines.add_weather import add_weather


async def process_media(image_path: Path, user_id: int, session: AsyncSession) -> None:
    print(f"{image_path.name.ljust(35)} > ", end="")

    image_info = base_info(image_path)
    print(".", end="")

    try:
        exif_info = add_exif_info(image_info)
        print(
            f"{readable_bytes(exif_info.size_bytes)}, {exif_info.width} x {exif_info.height}",
            end="",
        )
        if exif_info.duration is not None:
            print(f", {exif_info.duration}s", end="")
        print(".", end="")
    except ExifToolExecuteError:
        print(f"\nFailed to process {image_info}")
        return None

    await generate_thumbnails(image_info)
    print(".", end="")
    data_info = add_data_url(exif_info)
    print(".", end="")
    gps_info = add_gps_info(data_info)
    print(".", end="")
    time_info = add_time_taken(gps_info)
    print(".", end="")
    weather_info = add_weather(time_info)
    print(".", end="")

    await store_image(weather_info, user_id, session)
    print("!")

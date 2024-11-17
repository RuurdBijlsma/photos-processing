from pathlib import Path

# noinspection PyUnresolvedReferences
import pillow_avif
from PIL import Image
from exiftool.exceptions import ExifToolExecuteError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.db_utils import store_image
from app.data.interfaces.visual_information import BaseVisualInformation, \
    OcrVisualInformation
from app.processing.pipelines.frame_based.frame_embedding import frame_embedding
from app.processing.pipelines.frame_based.frame_ocr import frame_ocr
from app.processing.pipelines.generate_thumbnails import generate_thumbnails
from app.processing.pipelines.image_based.base_info import base_info
from app.processing.pipelines.image_based.image_data_url import image_data_url
from app.processing.pipelines.image_based.image_exif import image_exif_info
from app.processing.pipelines.image_based.image_gps import image_gps_info
from app.processing.pipelines.image_based.image_time_taken import image_time_taken
from app.processing.pipelines.image_based.image_weather import image_weather
from app.processing.process_utils import readable_bytes, pil_to_jpeg

max_thumb_height = max(app_config.thumbnail_heights)


async def process_media(image_path: Path, user_id: int, session: AsyncSession) -> None:
    print(f"{image_path.name.ljust(35)} > ", end="")

    image_info = base_info(image_path)
    print(".", end="")

    try:
        exif_info = image_exif_info(image_info)
        print(f"{readable_bytes(exif_info.size_bytes)}, "
              f"{exif_info.width} x {exif_info.height}", end="", )
        if exif_info.duration is not None:
            print(f", {exif_info.duration}s", end="")
        print(".", end="")
    except ExifToolExecuteError:
        print(f"\nFailed to process {image_info}")
        return None

    await generate_thumbnails(image_info)
    print(".", end="")
    thumbnail_path = (app_config.thumbnails_dir /
                      image_info.hash /
                      f"{max_thumb_height}p.avif")

    # processing that requires PIL Image (only 1st frame/main thumbnail for videos)
    with Image.open(thumbnail_path) as pil_image:
        data_info = image_data_url(exif_info, pil_image)

    # processing that must be done for multiple thumbnails in a video (ex. every 20%)
    # todo generate thumb every 20%
    #   and do this for every thumb
    visual_infos: list[OcrVisualInformation] = []
    with Image.open(thumbnail_path) as pil_image:
        jpeg_image = pil_to_jpeg(pil_image)

        visual_info = BaseVisualInformation(snapshot_time_ms=0)
        embed_info = frame_embedding(visual_info, jpeg_image)
        ocr_info = frame_ocr(embed_info, jpeg_image)
        visual_infos.append(ocr_info)

        jpeg_image.close()

    print(".", end="")
    gps_info = image_gps_info(data_info)
    print(".", end="")
    time_info = image_time_taken(gps_info)
    print(".", end="")
    weather_info = image_weather(time_info)
    print(".", end="")

    await store_image(weather_info, visual_infos, user_id, session)
    print("!")

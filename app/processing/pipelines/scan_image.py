from dataclasses import dataclass
from pathlib import Path

import PIL.Image
import pillow_avif  # noqa: F401

from app.config.app_config import app_config
from app.data.interfaces.image_info_types import WeatherImageInfo
from app.data.interfaces.visual_information import BaseVisualInformation, \
    ObjectsVisualInformation
from app.processing.pipelines.frame_based.frame_caption import frame_caption
from app.processing.pipelines.frame_based.frame_classification import \
    frame_classification
from app.processing.pipelines.frame_based.frame_embedding import frame_embedding
from app.processing.pipelines.frame_based.frame_faces import frame_faces
from app.processing.pipelines.frame_based.frame_object_detection import \
    frame_object_detection
from app.processing.pipelines.frame_based.frame_ocr import frame_ocr
from app.processing.pipelines.frame_based.frame_text_summary import frame_text_summary
from app.processing.pipelines.image_based.base_info import base_info
from app.processing.pipelines.image_based.image_data_url import image_data_url
from app.processing.pipelines.image_based.image_exif import image_exif_info
from app.processing.pipelines.image_based.image_gps import image_gps_info
from app.processing.pipelines.image_based.image_time_taken import image_time_taken
from app.processing.pipelines.image_based.image_weather import image_weather
from app.processing.processing.process_utils import readable_bytes, pil_to_jpeg, ImageThumbnails

max_thumb_height = max(app_config.thumbnail_heights)


@dataclass
class ScannableFrame:
    image_path: Path
    snapshot_time_ms: int = 0


def scan_image(
    image_path: Path,
    image_hash: str,
    thumbnails: ImageThumbnails
) -> tuple[WeatherImageInfo, list[ObjectsVisualInformation]]:
    print(f"{image_path.name.ljust(35)}")
    image_info = base_info(image_path, image_hash)
    exif_info = image_exif_info(image_info)

    print(f"{readable_bytes(exif_info.size_bytes)}, "
          f"{exif_info.width} x {exif_info.height}", end="", )
    if exif_info.duration is not None:
        print(f", {exif_info.duration}s")
    else:
        print()

    with PIL.Image.open(thumbnails.thumbnails[1080]) as thumbnail_image:
        data_info = image_data_url(exif_info, thumbnail_image)

    visual_infos: list[ObjectsVisualInformation] = []
    for frame_percentage, frame_image_path in thumbnails.frames.items():
        with PIL.Image.open(frame_image_path) as frame_image:
            jpeg_frame = pil_to_jpeg(frame_image)

        visual_info = BaseVisualInformation(frame_percentage=frame_percentage)
        embed_info = frame_embedding(visual_info, jpeg_frame)
        classify_info = frame_classification(embed_info, jpeg_frame)
        ocr_info = frame_ocr(classify_info, jpeg_frame)
        faces_info = frame_faces(ocr_info, jpeg_frame)
        summary_info = frame_text_summary(faces_info, jpeg_frame)
        caption_info = frame_caption(summary_info, jpeg_frame)
        objects_info = frame_object_detection(caption_info, jpeg_frame)
        visual_infos.append(objects_info)

        jpeg_frame.close()

    gps_info = image_gps_info(data_info)
    time_info = image_time_taken(gps_info)
    weather_info = image_weather(time_info)

    return weather_info, visual_infos

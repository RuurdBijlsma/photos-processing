import base64
from io import BytesIO

import pillow_avif  # type: ignore
from PIL import Image

from photos.config.app_config import app_config
from photos.data.interfaces.image_info_types import ExifImageInfo, DataUrlImageInfo

max_thumb_height = max(app_config.thumbnail_heights)


def add_data_url(image_info: ExifImageInfo) -> DataUrlImageInfo:
    with Image.open(
        app_config.thumbnails_dir / image_info.hash / f"{max_thumb_height}p.avif"
    ) as img:
        tiny_height = 6
        img = img.resize((int(img.width / img.height * tiny_height), tiny_height))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        return DataUrlImageInfo(**image_info.model_dump(), data_url=data_url)

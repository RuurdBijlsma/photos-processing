import base64
from io import BytesIO

from PIL import Image

from photos.config.app_config import app_config
from photos.data.interfaces.image_info_types import BaseImageInfo, DataUrlImageInfo


def add_data_url(image_info: BaseImageInfo) -> DataUrlImageInfo:
    with Image.open(app_config.images_dir / image_info.relative_path) as img:
        tiny_height = 6
        img.resize((int(img.width / img.height * tiny_height), tiny_height))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        return DataUrlImageInfo(
            **image_info.model_dump(),
            data_url=data_url
        )

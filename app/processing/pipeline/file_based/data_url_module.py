import base64
from io import BytesIO

import PIL
import pillow_avif  # noqa: F401

from app.config.app_config import app_config
from app.data.interfaces.image_data import DataUrlData, ImageData
from app.processing.pipeline.base_module import FileModule
from app.processing.processing.process_utils import get_thumbnail_paths


class DataUrlModule(FileModule):
    def process(self, data: ImageData) -> DataUrlData:
        thumbnail_paths = get_thumbnail_paths(
            app_config.images_dir / data.relative_path,
            data.hash,
        )

        tiny_height = 6
        with PIL.Image.open(
                thumbnail_paths.thumbnails[min(thumbnail_paths.thumbnails.keys())],
        ) as pil_image:
            img = pil_image.resize((
                int(pil_image.width / pil_image.height * tiny_height),
                tiny_height,
            ))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return DataUrlData(
            **data.model_dump(),
            data_url=f"data:image/png;base64,{img_str}",
        )

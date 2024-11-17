import base64
from io import BytesIO

from PIL.Image import Image

from photos.data.interfaces.image_info_types import ExifImageInfo, DataUrlImageInfo


def image_data_url(image_info: ExifImageInfo, pil_image: Image) -> DataUrlImageInfo:
    tiny_height = 6
    img = pil_image.resize((
        int(pil_image.width / pil_image.height * tiny_height),
        tiny_height
    ))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    data_url = f"data:image/png;base64,{img_str}"

    return DataUrlImageInfo(**image_info.model_dump(), data_url=data_url)

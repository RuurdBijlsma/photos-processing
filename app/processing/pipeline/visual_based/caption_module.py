from PIL.Image import Image

from app.config.app_config import app_config
from app.data.interfaces.visual_data import CaptionData, VisualData
from app.machine_learning.caption.get_captioner import get_captioner_by_provider
from app.processing.pipeline.base_module import VisualModule

captioner = get_captioner_by_provider(app_config.captions_provider)


class CaptionModule(VisualModule):
    def process(self, data: VisualData, image: Image) -> CaptionData:
        caption = captioner.caption(image)

        return CaptionData(
            **data.model_dump(),
            caption=caption,
        )

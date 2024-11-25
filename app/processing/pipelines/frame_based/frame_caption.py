from PIL.Image import Image

from app.config.app_config import app_config
from app.data.interfaces.visual_information import TextSummaryVisualInformation, \
    CaptionVisualInformation
from app.machine_learning.caption.get_captioner import get_captioner_by_provider

captioner = get_captioner_by_provider(app_config.captions_provider)


def frame_caption(
    visual_info: TextSummaryVisualInformation,
    pil_image: Image
) -> CaptionVisualInformation:
    caption = captioner.caption(pil_image)

    return CaptionVisualInformation(
        **visual_info.model_dump(),
        caption=caption
    )

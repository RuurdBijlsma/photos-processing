from PIL.Image import Image

from app.config.app_config import app_config
from app.data.interfaces.visual_information import CaptionVisualInformation, \
    FacesVisualInformation
from app.machine_learning.visual_llm.get_llm import get_llm_by_provider

llm = get_llm_by_provider(app_config.llm_provider)


def frame_caption(
    visual_info: FacesVisualInformation,
    pil_image: Image
) -> CaptionVisualInformation:
    if not app_config.enable_llm:
        return CaptionVisualInformation(
            **visual_info.model_dump(),
            caption=None
        )
    prompt = ("Describe this image in a way that captures all essential details "
              "for a search database. Include the setting, key objects, actions, "
              "number and type of people or animals, and any noticeable visual "
              "features. Make the description clear, concise, and useful for "
              "someone searching this image in a library. Avoid subjective "
              "interpretations or ambiguous terms.")

    caption = llm.image_question(pil_image, prompt)

    return CaptionVisualInformation(
        **visual_info.model_dump(),
        caption=caption
    )

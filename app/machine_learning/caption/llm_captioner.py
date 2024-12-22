from PIL.Image import Image

from app.config.config_types import LLMProvider
from app.machine_learning.caption.captioner_protocol import CaptionerProtocol
from app.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM
from app.machine_learning.visual_llm.get_llm import get_llm_by_provider


class LLMCaptioner(CaptionerProtocol):
    llm_provider: BaseVisualLLM
    prompt: str = (
        "You are a BLIP image captioning model. "
        "Generate a short caption for this image. "
        "Examples: 'A plate of hotdogs', "
        "'A bedroom with a bed and chair', "
        "'A group of people by a lake', "
        "'A tabby cat on a bed'. "
        "Only output the caption!"
    )

    def __init__(self, provider: LLMProvider) -> None:
        self.llm_provider = get_llm_by_provider(provider)

    def caption(self, image: Image) -> str:
        caption = self.llm_provider.image_question(
            image=image,
            question=self.prompt,
        )
        return caption.replace('"', "").replace("'", "")

from PIL.Image import Image

from app.config.app_config import app_config
from app.data.interfaces.visual_data import SummaryData, VisualData
from app.machine_learning.visual_llm.get_llm import get_llm_by_provider
from app.processing.pipeline.base_module import VisualModule

llm = get_llm_by_provider(app_config.llm_provider)


class SummaryModule(VisualModule):
    def process(self, data: VisualData, image: Image) -> SummaryData:
        if not app_config.enable_text_summary:
            return SummaryData(
                **data.model_dump(),
                summary=None,
            )
        prompt = ("Describe this image in a way that captures all essential details "
                  "for a search database. Include the setting, key objects, actions, "
                  "number and type of people or animals, and any noticeable visual "
                  "features. Make the description clear, concise, and useful for "
                  "someone searching this image in a library. Avoid subjective "
                  "interpretations or ambiguous terms.")

        caption = llm.image_question(image, prompt)

        return SummaryData(
            **data.model_dump(),
            summary=caption,
        )

from functools import lru_cache
from typing import ClassVar

from PIL.Image import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

from app.machine_learning.caption.captioner_protocol import CaptionerProtocol


@lru_cache
def get_processor_and_model() -> tuple[BlipProcessor, BlipForConditionalGeneration]:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")
    return processor, model


class BlipCaptioner(CaptionerProtocol):
    # dumbass blip captioner comes up with the word arafed or araffe sometimes.
    hallucinated_words: ClassVar[list[str]] = ["arafed", "araffe"]

    def caption(self, image: Image) -> str:
        caption = self.raw_caption(image)
        # Captions with apostrophe come out weird: "Person ' s"
        caption = caption.replace(" ' ", "'")
        if all(word not in caption for word in self.hallucinated_words):
            return caption.capitalize()
        for fake_word in self.hallucinated_words:
            caption = caption.replace(fake_word, "")
        return caption.strip().capitalize()

    @staticmethod
    def raw_caption(image: Image, conditional: str | None = None) -> str:
        processor, model = get_processor_and_model()
        rgb_image = image.convert("RGB")
        if conditional is None:
            inputs = processor(rgb_image, return_tensors="pt").to("cuda")
        else:
            inputs = processor(rgb_image, conditional, return_tensors="pt").to("cuda")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        assert isinstance(caption, str)
        return caption

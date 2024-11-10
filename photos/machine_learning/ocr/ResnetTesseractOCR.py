from functools import lru_cache

import torch
from PIL.Image import Image
from pytesseract import pytesseract
from transformers import (
    AutoModelForImageClassification,
    AutoImageProcessor,
    PreTrainedModel,
    ConvNextImageProcessor,
)

from photos.machine_learning.ocr.OCRProtocol import OCRProtocol


class ResnetTesseractOCR(OCRProtocol):
    @lru_cache
    def get_detector_model_and_processor(
        self,
    ) -> tuple[PreTrainedModel, ConvNextImageProcessor]:
        model = AutoModelForImageClassification.from_pretrained(
            "miguelcarv/resnet-152-text-detector"
        )
        processor = AutoImageProcessor.from_pretrained(
            "microsoft/resnet-50", do_resize=False
        )
        return model, processor

    def has_legible_text(self, image: Image) -> bool:
        resized_image = image.convert("RGB").resize((300, 300))
        model, processor = self.get_detector_model_and_processor()
        inputs = processor(resized_image, return_tensors="pt").pixel_values

        with torch.no_grad():
            outputs = model(inputs)
        logits_per_image = outputs.logits
        probs = logits_per_image.softmax(dim=1)
        has_legible_text = (probs[0][1] > probs[0][0]).item()
        assert isinstance(has_legible_text, bool)
        return has_legible_text

    def get_text(self, image: Image) -> str:
        extracted_text = pytesseract.image_to_string(image)
        assert isinstance(extracted_text, str)
        return extracted_text

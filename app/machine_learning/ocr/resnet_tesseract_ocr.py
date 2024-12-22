from functools import lru_cache

import torch
from PIL.Image import Image
from pytesseract import Output, pytesseract
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    ConvNextImageProcessor,
    PreTrainedModel,
)

from app.config.app_config import app_config
from app.data.interfaces.ml_types import OCRBox
from app.machine_learning.ocr.ocr_protocol import OCRProtocol
from app.machine_learning.utils import coordinate_to_proportional


@lru_cache
def get_detector_model_and_processor() -> tuple[
    PreTrainedModel, ConvNextImageProcessor,
]:
    model = AutoModelForImageClassification.from_pretrained(
        "miguelcarv/resnet-152-text-detector",
    )
    processor = AutoImageProcessor.from_pretrained(
        "microsoft/resnet-50", do_resize=False,
    )
    return model, processor


class ResnetTesseractOCR(OCRProtocol):

    def has_legible_text(self, image: Image) -> bool:
        resized_image = image.convert("RGB").resize((300, 300))
        model, processor = get_detector_model_and_processor()
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

    def get_boxes(self, image: Image) -> list[OCRBox]:
        ocr_data = pytesseract.image_to_data(
            image, lang="+".join(app_config.media_languages), output_type=Output.DICT,
        )

        boxes: list[OCRBox] = []
        for i in range(len(ocr_data["level"])):
            box = OCRBox(
                position=coordinate_to_proportional(
                    [ocr_data["left"][i], ocr_data["top"][i]], image,
                ),
                width=ocr_data["width"][i] / image.width,
                height=ocr_data["height"][i] / image.height,
                text=ocr_data["text"][i],
                confidence=ocr_data["conf"][i] / 100,
            )
            if box.text.strip() == "" or box.confidence < 0:
                continue
            boxes.append(box)

        return boxes

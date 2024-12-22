from typing import TYPE_CHECKING

from PIL.Image import Image

from app.config.app_config import app_config
from app.data.interfaces.visual_data import OCRData, VisualData
from app.machine_learning.ocr.resnet_tesseract_ocr import ResnetTesseractOCR
from app.machine_learning.visual_llm.get_llm import get_llm_by_provider
from app.processing.pipeline.base_module import VisualModule

if TYPE_CHECKING:
    from app.data.interfaces.ml_types import OCRBox

ocr = ResnetTesseractOCR()
llm = get_llm_by_provider(app_config.llm_provider)


class OCRModule(VisualModule):
    def process(self, data: VisualData, image: Image) -> OCRData:
        has_text = ocr.has_legible_text(image)
        extracted_text: str | None = None
        summary: str | None = None
        boxes: list[OCRBox] = []
        if has_text:
            extracted_text = ocr.get_text(image)
            if extracted_text.strip() == "":
                has_text = False
                extracted_text = None
            boxes = ocr.get_boxes(image)

        # Check if this could be a photo of a document
        if (
            app_config.enable_document_summary
            and has_text
            and extracted_text
            and len(extracted_text) > app_config.document_detection_threshold
        ):
            prompt = ("Analyze the image and provide the following details:\n\n"

                "Summary: A concise summary of the content in the photo, including any"
                "key points or important sections visible."
                "Text Detection: Detect and list any legible text visible in the image."
                "If possible, extract it and provide a short excerpt or the full text."
                "Language Detection: Identify the language(s) in the text and specify the"
                "primary language used."
                "Document Type: Determine the type of document or text. Is it a formal"
                "document (e.g., letter, contract, form), informal (e.g., note, memo),"
                "or something else? Provide details about the document's likely purpose"
                "(e.g., invoice, receipt, report, etc.)."
                "Text Formatting: If relevant, describe any specific formatting styles"
                "such as headings, bullet points, numbered lists, tables, or signatures."
                "Additional Features: Detect if there are any images, logos, or other"
                "non-text elements present that provide additional context or information"
                "about the document (e.g., company logos, photos, charts)."
                "Contextual Details: If applicable, mention any visible date, address,"
                "or other contextual information that could help understand the document's"
                "origin or purpose.")

            summary = llm.image_question(image, prompt)

        return OCRData(
            **data.model_dump(),
            has_legible_text=has_text,
            ocr_text=extracted_text,
            document_summary=summary,
            ocr_boxes=boxes,
        )

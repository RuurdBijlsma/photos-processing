from PIL.Image import Image

from app.data.interfaces.ml_types import OCRBox
from app.data.interfaces.visual_information import EmbeddingVisualInformation, \
    OcrVisualInformation
from app.machine_learning.embedding.CLIPEmbedder import CLIPEmbedder
from app.machine_learning.ocr.ResnetTesseractOCR import ResnetTesseractOCR

embedder = CLIPEmbedder()

ocr = ResnetTesseractOCR()


def frame_ocr(
    visual_info: EmbeddingVisualInformation,
    pil_image: Image
) -> OcrVisualInformation:
    has_text = ocr.has_legible_text(pil_image)
    extracted_text: str | None = None
    boxes: list[OCRBox] | None = None
    if has_text:
        extracted_text = ocr.get_text(pil_image)
        boxes = ocr.get_boxes(pil_image)

    return OcrVisualInformation(
        **visual_info.model_dump(),
        has_legible_text=has_text,
        ocr_text=extracted_text,
        # ocr_boxes=boxes
    )

from pydantic import BaseModel


class BaseVisualInformation(BaseModel):
    snapshot_time_ms: int


class EmbeddingVisualInformation(BaseVisualInformation):
    embedding: list[float]


class OcrVisualInformation(EmbeddingVisualInformation):
    has_legible_text: bool
    ocr_text: str | None
    document_summary: str | None
    # ocr_boxes: list[OCRBox] | None

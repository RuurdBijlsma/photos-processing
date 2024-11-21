from pydantic import BaseModel

from app.data.interfaces.ml_types import OCRBox, FaceBox, ObjectBox


class BaseVisualInformation(BaseModel):
    snapshot_time_ms: int


class EmbeddingVisualInformation(BaseVisualInformation):
    embedding: list[float]


class OCRVisualInformation(EmbeddingVisualInformation):
    has_legible_text: bool
    ocr_text: str | None
    document_summary: str | None
    ocr_boxes: list[OCRBox]


class FacesVisualInformation(OCRVisualInformation):
    faces: list[FaceBox]


class CaptionVisualInformation(FacesVisualInformation):
    caption: str


class ObjectsVisualInformation(CaptionVisualInformation):
    objects: list[ObjectBox]

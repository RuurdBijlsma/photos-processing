from pydantic import BaseModel

from app.data.enums.activity_type import ActivityType
from app.data.enums.document_type import DocumentType
from app.data.enums.scene_type import SceneType
from app.data.enums.weather_condition import WeatherCondition
from app.data.interfaces.ml_types import OCRBox, FaceBox, ObjectBox


class BaseVisualInformation(BaseModel):
    snapshot_time_ms: int


class EmbeddingVisualInformation(BaseVisualInformation):
    embedding: list[float]


class ClassificationVisualInformation(EmbeddingVisualInformation):
    is_selfie: bool
    is_pet: bool
    includes_animal: bool
    is_document: bool
    is_panorama: bool
    is_motion_photo: bool
    is_hdr: bool
    is_night_sight: bool
    is_activity: bool
    is_event: bool
    is_group_of_people: bool
    is_landscape: bool
    is_cityscape: bool
    is_food: bool
    is_travel: bool
    is_art: bool
    is_car: bool
    is_outside: bool

    weather: WeatherCondition | None
    scene_type: SceneType
    document_type: DocumentType | None
    activity_type: ActivityType | None


class OCRVisualInformation(ClassificationVisualInformation):
    has_legible_text: bool
    ocr_text: str | None
    document_summary: str | None
    ocr_boxes: list[OCRBox]


class FacesVisualInformation(OCRVisualInformation):
    faces: list[FaceBox]


class TextSummaryVisualInformation(FacesVisualInformation):
    summary: str | None


class CaptionVisualInformation(TextSummaryVisualInformation):
    caption: str


class ObjectsVisualInformation(CaptionVisualInformation):
    objects: list[ObjectBox]

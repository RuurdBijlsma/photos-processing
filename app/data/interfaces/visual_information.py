from pydantic import BaseModel

from app.data.enums.activity_type import ActivityType
from app.data.enums.animal_type import AnimalType
from app.data.enums.document_type import DocumentType
from app.data.enums.event_type import EventType
from app.data.enums.object_type import ObjectType
from app.data.enums.people_type import PeopleType
from app.data.enums.scene_type import SceneType
from app.data.enums.weather_condition import WeatherCondition
from app.data.interfaces.ml_types import OCRBox, FaceBox, ObjectBox


class BaseVisualInformation(BaseModel):
    frame_percentage: int


class EmbeddingVisualInformation(BaseVisualInformation):
    embedding: list[float]


class ClassificationVisualInformation(EmbeddingVisualInformation):
    scene_type: SceneType
    people_type: PeopleType | None
    animal_type: AnimalType | None
    document_type: DocumentType | None
    object_type: ObjectType | None
    activity_type: ActivityType | None
    event_type: EventType | None
    weather_condition: WeatherCondition | None
    is_outside: bool
    is_landscape: bool
    is_cityscape: bool
    is_travel: bool


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

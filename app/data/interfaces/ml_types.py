from enum import StrEnum

from pydantic import BaseModel

from app.data.enums.face_sex import FaceSex


class BaseBoundingBox(BaseModel):
    # position, width, height are proportional to full image width/height
    position: tuple[float, float]
    width: float
    height: float
    confidence: float


class ObjectBox(BaseBoundingBox):
    label: str


class OCRBox(BaseBoundingBox):
    text: str



class FaceBox(BaseBoundingBox):
    age: int
    sex: FaceSex
    mouth_left: tuple[float, float]
    mouth_right: tuple[float, float]
    nose_tip: tuple[float, float]
    eye_left: tuple[float, float]
    eye_right: tuple[float, float]
    embedding: list[float]

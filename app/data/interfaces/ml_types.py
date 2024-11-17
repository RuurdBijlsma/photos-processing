from enum import StrEnum

from pydantic import BaseModel


class OCRBox(BaseModel):
    position: tuple[float, float]
    # width, height are proportional to full image width/height
    width: float
    height: float
    text: str
    confidence: int


class FaceSex(StrEnum):
    Male = "M"
    Female = "F"


class FaceBox(BaseModel):
    position: tuple[float, float]
    # width, height are proportional to full image width/height
    width: float
    height: float
    age: int
    confidence: float
    sex: FaceSex
    mouth_left: tuple[float, float]
    mouth_right: tuple[float, float]
    nose_tip: tuple[float, float]
    eye_left: tuple[float, float]
    eye_right: tuple[float, float]
    embedding: list[float]

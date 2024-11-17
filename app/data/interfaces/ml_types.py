from enum import StrEnum

from pydantic import BaseModel


class Coordinate(BaseModel):
    # coordinates are proportional to full image width/height
    #   so a bounding box starting at 500px on a 1000px wide image will have x=0.5
    x: float
    y: float


class OCRBox(BaseModel):
    position: Coordinate
    # width, height are proportional to full image width/height
    width: float
    height: float
    text: str
    confidence: int


class FaceSex(StrEnum):
    Male = ("M",)
    Female = "F"


class FaceBox(BaseModel):
    position: Coordinate
    # width, height are proportional to full image width/height
    width: float
    height: float
    age: int
    confidence: float
    sex: FaceSex
    mouth_left: Coordinate
    mouth_right: Coordinate
    nose_tip: Coordinate
    eye_left: Coordinate
    eye_right: Coordinate
    embedding: list[float]

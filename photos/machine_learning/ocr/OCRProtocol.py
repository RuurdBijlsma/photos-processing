from dataclasses import dataclass
from typing import Protocol

from PIL.Image import Image


@dataclass
class OCRBox:
    top: int
    left: int
    width: int
    height: int
    text: str
    confidence: int


class OCRProtocol(Protocol):
    def has_legible_text(self, image: Image) -> bool:
        """Check if an image has legible text."""
        ...

    def get_text(self, image: Image) -> str:
        """Extract text from an image using OCR."""
        ...

    def get_boxes(self, image: Image) -> list[OCRBox]: ...

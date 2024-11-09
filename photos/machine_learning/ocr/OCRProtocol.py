from typing import Protocol

from PIL.ImageFile import ImageFile


class OCRProtocol(Protocol):
    def has_legible_text(self, image: ImageFile) -> bool:
        """Check if an image has legible text."""
        ...

    def get_text(self, image: ImageFile) -> str:
        """Extract text from an image using OCR."""
        ...

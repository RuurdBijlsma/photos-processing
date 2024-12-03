from typing import Protocol

from PIL.Image import Image

from app.data.interfaces.ml_types import ObjectBox


class ObjectDetectionProtocol(Protocol):
    def detect_objects(self, image: Image) -> list[ObjectBox]:
        """Check if an image has legible text."""

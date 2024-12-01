from typing import Protocol

from PIL.Image import Image


class CaptionerProtocol(Protocol):
    def caption(self, image: Image) -> str:
        ...

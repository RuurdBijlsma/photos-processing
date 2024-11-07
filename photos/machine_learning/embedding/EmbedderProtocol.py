from typing import Protocol

from PIL.ImageFile import ImageFile
from torch import Tensor


class EmbedderProtocol(Protocol):
    def embed_text(self, text: str) -> Tensor:
        """Embed a text input and return a list of floats as the embedding."""
        ...

    def embed_texts(self, texts: list[str]) -> Tensor:
        """Embed a text inputs."""
        ...

    def embed_image(self, image: ImageFile) -> Tensor:
        """Embed an image input and return a list of floats as the embedding."""
        ...

    def embed_images(self, images: list[ImageFile]) -> Tensor:
        """Embed images."""
        ...

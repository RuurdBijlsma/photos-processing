from typing import Protocol

from PIL.Image import Image
from torch import Tensor


class EmbedderProtocol(Protocol):
    def embed_text(self, text: str) -> Tensor:
        """Embed a text input and return a list of floats as the embedding."""
        ...

    def embed_texts(self, texts: list[str]) -> Tensor:
        """Embed a text inputs."""
        ...

    def embed_image(self, image: Image) -> Tensor:
        """Embed an image input and return a list of floats as the embedding."""
        ...

    def embed_images(self, images: list[Image]) -> Tensor:
        """Embed images."""
        ...

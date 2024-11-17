from typing import Protocol

from PIL.Image import Image


class EmbedderProtocol(Protocol):
    def embed_text(self, text: str) -> list[float]:
        """Embed a text input and return a list of floats as the embedding."""
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a text inputs."""
        ...

    def embed_image(self, image: Image) -> list[float]:
        """Embed an image input and return a list of floats as the embedding."""
        ...

    def embed_images(self, images: list[Image]) -> list[list[float]]:
        """Embed images."""
        ...

from typing import Protocol

import numpy as np
from PIL.Image import Image


class EmbedderProtocol(Protocol):
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a text input and return a list of floats as the embedding."""
        ...

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed a text inputs."""
        ...

    def embed_image(self, image: Image) -> np.ndarray:
        """Embed an image input and return a list of floats as the embedding."""
        ...

    def embed_images(self, images: list[Image]) -> np.ndarray:
        """Embed images."""
        ...

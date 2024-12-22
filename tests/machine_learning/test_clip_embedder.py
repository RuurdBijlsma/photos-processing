from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image

from app.machine_learning.embedding.clip_embedder import CLIPEmbedder


@pytest.fixture(scope="module")
def setup_embedder(
    assets_folder: Path,
) -> tuple[CLIPEmbedder, list[Image.Image], NDArray[Any]]:
    embedder = CLIPEmbedder()

    # Load images and create embeddings
    cat_img = Image.open(assets_folder / "cat.jpg")
    cluster_img = Image.open(assets_folder / "cluster.jpg")
    sunset_img = Image.open(assets_folder / "sunset.jpg")
    images: list[Image.Image] = [cat_img, cluster_img, sunset_img]
    images_embedding = embedder.embed_images(images)

    return embedder, images, images_embedding


@pytest.mark.parametrize(
    ("query", "img_index"),
    [
        ("A sunset over naples.", 2),  # Index 2 corresponds to sunset_img
        ("A cat sleeping in a bed.", 0),  # Index 0 corresponds to cat_img
        (
            "A cluster of raspberry pis in front of a laptop.",
            1,
        ),  # Index 1 corresponds to cluster_img
    ],
)
def test_clip_embedder(
    setup_embedder: tuple[
        CLIPEmbedder, list[Image.Image], NDArray[Any],
    ],
    query: str,
    img_index: int,
) -> None:
    embedder, _, images_embedding = setup_embedder

    text_embedding = embedder.embed_text(query)
    # Calculate cosine similarities between text and each image
    similarities = images_embedding @ np.array(text_embedding)
    # Assert the highest similarity index matches the expected image index
    assert np.argmax(similarities).item() == img_index

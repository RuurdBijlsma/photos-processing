from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from torch import Tensor

from photos.machine_learning.embedding.CLIPEmbedder import CLIPEmbedder


@pytest.fixture(scope="module")
def setup_embedder(
    tests_folder: Path,
) -> tuple[CLIPEmbedder, list[Image.Image], Tensor]:
    embedder = CLIPEmbedder()

    # Load images and create embeddings
    cat_img = Image.open(tests_folder / "assets/cat.jpg")
    cluster_img = Image.open(tests_folder / "assets/cluster.jpg")
    sunset_img = Image.open(tests_folder / "assets/sunset.jpg")
    images: list[Image.Image] = [cat_img, cluster_img, sunset_img]
    images_embedding = embedder.embed_images(images)

    return embedder, images, images_embedding


@pytest.mark.parametrize(
    "query, img_index",
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
    setup_embedder: tuple[CLIPEmbedder, list[Image.Image], Tensor],
    query: str,
    img_index: int,
) -> None:
    embedder, images, images_embedding = setup_embedder

    text_embedding = embedder.embed_text(query).unsqueeze(0)
    # Calculate cosine similarities between text and each image
    similarities = (images_embedding @ text_embedding.T).squeeze(1)  # Shape: (3,)
    # Assert the highest similarity index matches the expected image index
    assert np.argmax(similarities).item() == img_index

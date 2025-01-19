from pathlib import Path

import numpy as np
from media_analyzer import CLIPEmbedder
from PIL import Image

from app.processing.hdbscan_clustering import perform_clustering


def test_clustering(assets_folder: Path) -> None:
    image_names = [
        "flower.jpg",
        "mountain.jpg",
        "statue.jpg",
        "cat1.jpg",
        "cat2.jpg",
        "cat3.jpg",
        "cat_sleep1.jpg",
        "cat_sleep2.jpg",
        "cat_sleep3.jpg",
    ]
    embedder = CLIPEmbedder()
    images = [Image.open(assets_folder / image_name) for image_name in image_names]
    embeddings = [embedder.embed_image(image) for image in images]
    labels = perform_clustering(
        np.vstack(embeddings),
        min_samples=1,
        min_cluster_size=2,
    )
    assert isinstance(labels, list)
    # -1: can't find cluster
    # 0: cat cluster (not laying stretched out)
    # 1: cat cluster (stretched out)
    assert labels == [-1, -1, -1, 0, 0, 0, 1, 1, 1]

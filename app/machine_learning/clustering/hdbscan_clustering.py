from functools import lru_cache

import hdbscan
import numpy as np


@lru_cache
def get_clusterer(min_samples: int, min_cluster_size: int):
    return hdbscan.HDBSCAN(min_samples=min_samples, min_cluster_size=min_cluster_size,
                           metric="euclidean")


def perform_clustering(
    embeddings: np.ndarray,
    min_samples=5,
    min_cluster_size=10
):
    cluster_labels = get_clusterer(min_samples, min_cluster_size).fit_predict(
        embeddings)
    return cluster_labels

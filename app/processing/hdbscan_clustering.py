from functools import lru_cache
from typing import Any

import hdbscan
from numpy.typing import NDArray
from sklearn import preprocessing


@lru_cache
def get_clusterer(
    min_samples: int,
    min_cluster_size: int,
    prediction_data: bool,
    cluster_selection_method: str = "eom",
    cluster_selection_epsilon: float = 0.0,
) -> hdbscan.HDBSCAN:
    return hdbscan.HDBSCAN(
        min_samples=min_samples,
        min_cluster_size=min_cluster_size,
        prediction_data=prediction_data,
        cluster_selection_epsilon=cluster_selection_epsilon,
        cluster_selection_method=cluster_selection_method,
        metric="euclidean",
    )


def perform_clustering(
    embeddings: NDArray[Any],
    min_samples: int = 5,
    min_cluster_size: int = 10,
    cluster_selection_method: str = "eom",
    cluster_selection_epsilon: float = 0.0,
) -> list[int]:
    # l2 normalize, so that euclidean metric will work similar to cosine metric would
    #   cosine is not supported in hdbscan
    normalized = preprocessing.normalize(embeddings)
    clusterer = get_clusterer(
        min_samples,
        min_cluster_size,
        False,
        cluster_selection_method=cluster_selection_method,
        cluster_selection_epsilon=cluster_selection_epsilon,
    )
    cluster_labels = clusterer.fit_predict(normalized)
    cluster_list = cluster_labels.tolist()
    assert isinstance(cluster_list, list)
    return cluster_list

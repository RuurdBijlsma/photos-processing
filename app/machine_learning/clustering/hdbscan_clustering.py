from functools import lru_cache
from pathlib import Path
from typing import Any

import hdbscan
import joblib
import numpy as np
from hdbscan import approximate_predict
from sklearn import preprocessing


def invalidate_cache(func: Any, *args: Any) -> None:
    try:
        key = func.cache_key(*args)
        del func.cache_info()._cache[key]
        print(f"Cache invalidated for input: {args}")
    except KeyError:
        print(f"No cache entry found for input: {args}")
    except AttributeError:
        print(f"Function {func} has no cache yet.")


@lru_cache
def get_clusterer(
    min_samples: int,
    min_cluster_size: int,
    prediction_data: bool,
    cluster_selection_method: str = 'eom',
    cluster_selection_epsilon: float = 0.0,
) -> hdbscan.HDBSCAN:
    return hdbscan.HDBSCAN(
        min_samples=min_samples,
        min_cluster_size=min_cluster_size,
        prediction_data=prediction_data,
        cluster_selection_epsilon=cluster_selection_epsilon,
        cluster_selection_method=cluster_selection_method,
        metric="euclidean"
    )


@lru_cache
def get_cached_clusterer(file: Path) -> hdbscan.HDBSCAN:
    return joblib.load(file)


def predict_new_point(embedding: np.ndarray, cache_file: Path) -> int:
    # This isn't used for now, full clustering seems fast enough.
    if not cache_file.exists():
        raise FileNotFoundError(f"Clusterer cache file does not exist {cache_file}")
    loaded_clusterer = get_cached_clusterer(cache_file)
    labels, probabilities = approximate_predict(
        loaded_clusterer,
        [embedding]
    )
    label = labels[0].item()
    assert isinstance(label, int)
    return label


def perform_clustering(
    embeddings: np.ndarray,
    min_samples: int = 5,
    min_cluster_size: int = 10,
    cluster_selection_method: str = 'eom',
    cluster_selection_epsilon: float = 0.0,
    cache_file: Path | None = None
) -> list[int]:
    # l2 normalize, so that euclidean metric will work similar to cosine metric would
    #   cosine is not supported in hdbscan
    normalized = preprocessing.normalize(embeddings)
    clusterer = get_clusterer(
        min_samples,
        min_cluster_size,
        cache_file is not None,
        cluster_selection_method=cluster_selection_method,
        cluster_selection_epsilon=cluster_selection_epsilon,
    )
    cluster_labels = clusterer.fit_predict(normalized)
    if cache_file is not None:
        out_folder = cache_file.parent
        if not out_folder.exists():
            out_folder.mkdir(parents=True)
        invalidate_cache(get_cached_clusterer, cache_file)
        joblib.dump(clusterer, cache_file)
    assert isinstance(cluster_labels, list)
    return cluster_labels

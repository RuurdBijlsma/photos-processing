from functools import lru_cache
from pathlib import Path
from typing import Callable, Any

import hdbscan
import joblib
import numpy as np
from hdbscan import approximate_predict
from sklearn import preprocessing


def invalidate_cache(func: Callable, *args: Any):
    try:
        key = func.cache_key(*args)
        del func.cache_info()._cache[key]
        print(f"Cache invalidated for input: {args}")
    except KeyError:
        print(f"No cache entry found for input: {args}")
    except AttributeError:
        print(f"Function {func} has no cache yet.")


@lru_cache
def get_clusterer(min_samples: int, min_cluster_size: int, prediction_data: bool):
    return hdbscan.HDBSCAN(
        min_samples=min_samples,
        min_cluster_size=min_cluster_size,
        prediction_data=True,
        metric="euclidean"
    )


@lru_cache
def get_cached_clusterer(file: Path) -> hdbscan.HDBSCAN:
    return joblib.load(file)


def predict_new_point(embedding: np.ndarray, cache_file: Path):
    # This isn't used for now, full clustering seems fast enough.
    if not cache_file.exists():
        raise FileNotFoundError(f"Clusterer cache file does not exist {cache_file}")
    loaded_clusterer = get_cached_clusterer(cache_file)
    labels, probabilities = approximate_predict(
        loaded_clusterer,
        [embedding]
    )
    return labels[0].item()


def perform_clustering(
    embeddings: np.ndarray,
    min_samples=5,
    min_cluster_size=10,
    cache_file: Path | None = None
):
    normalized = preprocessing.normalize(embeddings)
    clusterer = get_clusterer(
        min_samples,
        min_cluster_size,
        cache_file is not None,
    )
    cluster_labels = clusterer.fit_predict(normalized)
    if cache_file is not None:
        out_folder = cache_file.parent
        if not out_folder.exists():
            out_folder.mkdir(parents=True)
        invalidate_cache(get_cached_clusterer, cache_file)
        joblib.dump(clusterer, cache_file)
    return cluster_labels

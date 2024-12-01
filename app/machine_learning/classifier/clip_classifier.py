from functools import lru_cache

import numpy as np
from scipy.special import softmax
from sklearn.metrics.pairwise import cosine_similarity

from app.machine_learning.classifier.base_classifier import BaseClassifier
from app.machine_learning.embedding.clip_embedder import CLIPEmbedder

embedder = CLIPEmbedder()


@lru_cache
def cached_embed_text(text: str) -> np.ndarray:
    return embedder.embed_text(text)


class CLIPClassifier(BaseClassifier):
    def classify_image(
        self,
        image_embedding: np.ndarray,
        classes: list[str]
    ) -> tuple[int, float]:
        text_embeddings = [cached_embed_text(c) for c in classes]
        similarities = cosine_similarity([image_embedding], text_embeddings)
        normalized: np.ndarray = softmax(similarities)
        best_index = np.argmax(normalized)
        confidence = normalized[0, best_index].item()
        return int(best_index), confidence

    def binary_classify_image(
        self,
        image_embedding: np.ndarray,
        positive_prompt: str,
        negative_prompt: str
    ) -> tuple[bool, float]:
        index, confidence = self.classify_image(
            image_embedding,
            [negative_prompt, positive_prompt]
        )
        return bool(index), confidence

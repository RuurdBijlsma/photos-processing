from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TypeVar

import numpy as np

TEnum = TypeVar("TEnum", bound=StrEnum)


class BaseClassifier(ABC):
    @abstractmethod
    def classify_image(
        self,
        image_embedding: np.ndarray,
        classes: list[str]
    ) -> tuple[int, float]:
        ...

    @abstractmethod
    def binary_classify_image(
        self,
        image_embedding: np.ndarray,
        positive_prompt: str,
        negative_prompt: str
    ) -> tuple[bool, float]:
        ...

    def classify_to_enum(
        self,
        image_embedding: np.ndarray,
        positive_prompt: str,
        negative_prompt: str,
        enum_type: type[TEnum]
    ) -> TEnum | None:
        is_enum = self.binary_classify_image(
            image_embedding,
            positive_prompt,
            negative_prompt
        )
        if not is_enum:
            return None

        best_index, _ = self.classify_image(
            image_embedding,
            [e.value.replace("_", " ") for e in enum_type]
        )
        return list(enum_type)[best_index]

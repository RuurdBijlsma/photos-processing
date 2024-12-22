from abc import ABC, abstractmethod
from enum import Enum, StrEnum
from typing import Any, TypeVar

from numpy.typing import NDArray

TStrEnum = TypeVar("TStrEnum", bound=StrEnum)
TEnum = TypeVar("TEnum", bound=Enum)


class BaseClassifier(ABC):
    @abstractmethod
    def classify_image(
        self,
        image_embedding: NDArray[Any],
        classes: list[str],
    ) -> tuple[int, float]:
        ...

    @abstractmethod
    def binary_classify_image(
        self,
        image_embedding: NDArray[Any],
        positive_prompt: str,
        negative_prompt: str,
    ) -> tuple[bool, float]:
        ...

    def classify_to_enum_with_descriptions(
        self,
        image_embedding: NDArray[Any],
        positive_prompt: str | None,
        negative_prompt: str | None,
        class_descriptions: dict[TEnum, str],
    ) -> TEnum | None:
        if positive_prompt is not None and negative_prompt is not None:
            is_enum, _ = self.binary_classify_image(
                image_embedding,
                positive_prompt,
                negative_prompt,
            )
            if not is_enum:
                return None

        best_index, _ = self.classify_image(
            image_embedding,
            list(class_descriptions.values()),
        )
        return list(class_descriptions.keys())[best_index]

    def classify_to_enum(
        self,
        image_embedding: NDArray[Any],
        positive_prompt: str,
        negative_prompt: str,
        enum_type: type[TStrEnum],
    ) -> TStrEnum | None:
        is_enum, _ = self.binary_classify_image(
            image_embedding,
            positive_prompt,
            negative_prompt,
        )
        if not is_enum:
            return None

        best_index, _ = self.classify_image(
            image_embedding,
            [e.value.replace("_", " ") for e in enum_type],
        )
        return list(enum_type)[best_index]

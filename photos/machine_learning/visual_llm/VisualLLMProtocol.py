from collections.abc import Generator
from dataclasses import field, dataclass
from enum import StrEnum, auto
from typing import Protocol

from PIL.Image import Image
from PIL.Image import Image


class ChatRole(StrEnum):
    ASSISTANT = auto()
    USER = auto()


@dataclass
class ChatMessage:
    message: str
    images: list[Image] = field(default_factory=list)
    role: ChatRole = ChatRole.USER


class VisualLLMProtocol(Protocol):
    def image_question(self, image: Image, question: str) -> str:
        ...

    def images_question(self, images: list[Image], question: str) -> str:
        ...

    def chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: Image | None = None,
        convert_images: bool = True,
        temperature=0.7,
    ) -> tuple[str, list[ChatMessage]]:
        ...

    def stream_chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: Image | None = None,
        convert_images: bool = True,
        temperature=0.7,
    ) -> Generator[str, None, None]:
        ...

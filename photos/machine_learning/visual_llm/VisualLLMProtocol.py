from dataclasses import field, dataclass
from enum import StrEnum, auto
from typing import Protocol

from PIL.ImageFile import ImageFile


class ChatRole(StrEnum):
    ASSISTANT = auto()
    USER = auto()


@dataclass
class ChatMessage:
    message: str
    role: ChatRole = ChatRole.USER
    images: list[ImageFile] = field(default_factory=list)


class VisualLLMProtocol(Protocol):
    def image_question(self, image: ImageFile, question: str) -> str:
        ...

    def images_question(self, images: list[ImageFile], question: str) -> str:
        ...

    def chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: ImageFile | None = None
    ) -> tuple[str, list[ChatMessage]]:
        ...

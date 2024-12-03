from collections.abc import Generator
from functools import lru_cache

import torch
from PIL.Image import Image
from transformers import (
    PreTrainedModel,
    AutoModel,
    AutoTokenizer,
    PreTrainedTokenizerFast,
)

from app.machine_learning.visual_llm.visual_llm_protocol import VisualLLMProtocol, \
    ChatMessage, ChatRole


@lru_cache
def get_model_and_tokenizer() -> tuple[PreTrainedModel, PreTrainedTokenizerFast]:
    with torch.no_grad():
        model = AutoModel.from_pretrained(
            "openbmb/MiniCPM-V-2_6-int4", trust_remote_code=True
        )
        model.eval()
        if torch.cuda.is_available():
            model.to(torch.device("cuda"))
        elif torch.backends.mps.is_available():
            model.to(torch.device("mps"))
    tokenizer = AutoTokenizer.from_pretrained(
        "openbmb/MiniCPM-V-2_6-int4", trust_remote_code=True
    )
    return model, tokenizer


class MiniCPMLLM(VisualLLMProtocol):

    def image_question(self, image: Image, question: str) -> str:
        answer, _ = self.chat(ChatMessage(message=question, images=[image]))
        return answer

    def images_question(self, images: list[Image], question: str) -> str:
        answer, _ = self.chat(ChatMessage(message=question, images=images))
        return answer

    def chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: Image | None = None,
        convert_images: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> tuple[str, list[ChatMessage]]:
        if history is None:
            history = []
        messages = history + [message]

        answer = self._chat(
            message,
            history,
            image,
            convert_images,
            temperature,
            stream=False
        )
        assert isinstance(answer, str)
        return answer, messages + [ChatMessage(message=answer, role=ChatRole.ASSISTANT)]

    def stream_chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: Image | None = None,
        convert_images: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Generator[str, None, None]:
        result = self._chat(
            message,
            history,
            image,
            convert_images,
            temperature,
            stream=True
        )
        assert isinstance(result, Generator)
        return result

    def _chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: Image | None = None,
        convert_images: bool = True,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Generator[str, None, None] | str:
        if history is None:
            history = []

        if convert_images:
            rgb_image = image.convert("RGB") if image is not None else None
            for msg in history:
                msg.images = [image.convert("RGB") for image in msg.images]
            message.images = [image.convert("RGB") for image in message.images]
        else:
            rgb_image = image

        model, tokenizer = get_model_and_tokenizer()
        messages = history + [message]
        formatted_msgs = [
            {"role": msg.role.value.lower(), "content": msg.images + [msg.message]}
            for msg in messages
        ]
        result = model.chat(
            image=rgb_image,
            msgs=formatted_msgs,
            tokenizer=tokenizer,
            sampling=stream if stream else None,
            temperature=temperature,
            stream=stream,
        )
        assert isinstance(result, str | Generator)
        return result

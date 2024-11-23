import base64
from collections.abc import Generator
from io import BytesIO

from PIL.Image import Image
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from app.machine_learning.visual_llm.MiniCPMLLM import MiniCPMLLM
from app.machine_learning.visual_llm.VisualLLMProtocol import (
    ChatMessage, ChatRole,
)


def to_base64_url(image: Image, max_size=720):
    image.thumbnail((max_size, max_size))
    buffered = BytesIO()
    image.save(buffered, format="JPEG", optimize=True)
    b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def chat_to_dict(chat: ChatMessage) -> dict:
    if len(chat.images) == 0:
        return {
            "role": str(chat.role),
            "content": chat.message,
        }

    images = [
        {"type": "image_url", "image_url": {"url": to_base64_url(image)}}
        for image in chat.images
    ]
    result = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": chat.message,
            },
            *images
        ]
    }
    return result


class OpenAILLM(MiniCPMLLM):
    model_name: str
    client: OpenAI

    def __init__(self, model_name="gpt-4o-mini"):
        self.model_name = model_name
        self.client = OpenAI()

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

        response = self._chat_openai(
            message,
            history,
            temperature,
            max_tokens,
            stream=False
        )
        assert isinstance(response, ChatCompletion)
        answer = response.choices[0].message.content
        assert answer is not None
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
        response = self._chat_openai(
            message,
            history,
            temperature,
            max_tokens,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _chat_openai(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        if history is None:
            history = []
        messages = history + [message]
        dict_messages = list(map(chat_to_dict, messages))

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=dict_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
        )

        return response

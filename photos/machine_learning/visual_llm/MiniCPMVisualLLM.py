from functools import lru_cache

import torch
from PIL.ImageFile import ImageFile
from transformers import PreTrainedModel, AutoModel, AutoTokenizer, PreTrainedTokenizerFast

from photos.machine_learning.visual_llm.VisualLLMProtocol import VisualLLMProtocol, ChatMessage, ChatRole


class MiniCPMVisualLLM(VisualLLMProtocol):
    @lru_cache
    def get_model_and_tokenizer(self) -> tuple[PreTrainedModel, PreTrainedTokenizerFast]:
        model = AutoModel.from_pretrained('openbmb/MiniCPM-V-2_6', trust_remote_code=True,
                                          attn_implementation='sdpa',
                                          torch_dtype=torch.bfloat16)
        model = model.eval()
        if torch.cuda.is_available():
            model = model.cuda()
        tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-V-2_6', trust_remote_code=True)
        return model, tokenizer

    def image_question(self, image: ImageFile, question: str) -> str:
        answer, _ = self.chat(ChatMessage(message=question, images=[image]))
        return answer

    def images_question(self, images: list[ImageFile], question: str) -> str:
        answer, _ = self.chat(ChatMessage(message=question, images=images))
        return answer

    def chat(
        self,
        message: ChatMessage,
        history: list[ChatMessage] | None = None,
        image: ImageFile | None = None,
        convert_images: bool = True,
    ) -> tuple[str, list[ChatMessage]]:
        if history is None:
            history = []

        if convert_images:
            rgb_image = image.convert("RGB") if image is not None else None
            for message in history:
                message.images = [image.convert("RGB") for image in message.images]
            message.images = [image.convert("RGB") for image in message.images]
        else:
            rgb_image = image

        model, tokenizer = self.get_model_and_tokenizer()
        messages = history + [message]
        formatted_msgs = [
            {'role': msg.role.value.lower(), 'content': msg.images + [msg.message]}
            for msg in messages
        ]
        answer = model.chat(
            image=rgb_image,
            msgs=formatted_msgs,
            tokenizer=tokenizer,
        )
        updated_messages = messages + [ChatMessage(role=ChatRole.ASSISTANT, message=answer)]
        return answer, updated_messages

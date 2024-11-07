from functools import lru_cache

import torch
import torch.nn.functional as F
from PIL.ImageFile import ImageFile
from torch import Tensor
from transformers import CLIPModel, CLIPProcessor, PreTrainedModel

from photos.machine_learning.embedding.EmbedderProtocol import EmbedderProtocol


class CLIPEmbedder(EmbedderProtocol):
    @lru_cache
    def get_model_and_processor(self) -> tuple[PreTrainedModel, CLIPProcessor]:
        model = CLIPModel.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
        processor = CLIPProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
        assert isinstance(processor, CLIPProcessor)
        return model, processor

    def embed_text(self, text: str) -> Tensor:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> Tensor:
        model, processor = self.get_model_and_processor()
        inputs_text = processor(text=texts, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_embedding = model.get_text_features(**inputs_text)
        return F.normalize(text_embedding, p=2, dim=-1)

    def embed_image(self, image: ImageFile) -> Tensor:
        return self.embed_images([image])[0]

    def embed_images(self, images: list[ImageFile]) -> Tensor:
        model, processor = self.get_model_and_processor()
        inputs_image = processor(images=images, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_embedding = model.get_image_features(**inputs_image)
        return F.normalize(text_embedding, p=2, dim=-1)

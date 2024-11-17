from functools import lru_cache

import torch
import torch.nn.functional as F
from PIL.Image import Image
from transformers import CLIPModel, CLIPProcessor, PreTrainedModel

from app.machine_learning.embedding.EmbedderProtocol import EmbedderProtocol


@lru_cache
def get_model_and_processor() -> tuple[PreTrainedModel, CLIPProcessor]:
    model = CLIPModel.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
    processor = CLIPProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
    assert isinstance(processor, CLIPProcessor)
    return model, processor


class CLIPEmbedder(EmbedderProtocol):

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        model, processor = get_model_and_processor()
        inputs_text = processor(text=texts, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_embedding = model.get_text_features(**inputs_text)
        return F.normalize(text_embedding, p=2, dim=-1).tolist()

    def embed_image(self, image: Image) -> list[float]:
        return self.embed_images([image])[0]

    def embed_images(self, images: list[Image]) -> list[list[float]]:
        model, processor = get_model_and_processor()
        inputs_image = processor(images=images, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_embedding = model.get_image_features(**inputs_image)
        return F.normalize(text_embedding, p=2, dim=-1).tolist()

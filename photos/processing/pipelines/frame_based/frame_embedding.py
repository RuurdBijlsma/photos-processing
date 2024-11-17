from PIL.Image import Image

from photos.data.interfaces.visual_information import BaseVisualInformation, \
    EmbeddingVisualInformation
from photos.machine_learning.embedding.CLIPEmbedder import CLIPEmbedder

embedder = CLIPEmbedder()


def frame_embedding(
    visual_info: BaseVisualInformation,
    pil_image: Image
) -> EmbeddingVisualInformation:
    embedding = embedder.embed_image(pil_image)
    return EmbeddingVisualInformation(
        **visual_info.model_dump(),
        embedding=embedding
    )

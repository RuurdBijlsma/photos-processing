from PIL.Image import Image

from app.data.interfaces.visual_data import EmbeddingData, VisualData
from app.machine_learning.embedding.clip_embedder import CLIPEmbedder
from app.processing.pipeline.base_module import VisualModule

embedder = CLIPEmbedder()


class EmbeddingModule(VisualModule):
    def process(self, data: VisualData, image: Image) -> EmbeddingData:
        embedding = embedder.embed_image(image)
        return EmbeddingData(
            **data.model_dump(),
            embedding=embedding.tolist(),  # type: ignore[arg-type]
        )

from PIL.Image import Image

from app.data.interfaces.visual_data import FacesData, VisualData
from app.machine_learning.facial_recognition.insight_facial_recognition import (
    InsightFacialRecognition,
)
from app.processing.pipeline.base_module import VisualModule

facial_recognition = InsightFacialRecognition()


class FacesModule(VisualModule):
    def process(self, data: VisualData, image: Image) -> FacesData:
        faces = facial_recognition.get_faces(image)

        return FacesData(
            **data.model_dump(),
            faces=faces,
        )

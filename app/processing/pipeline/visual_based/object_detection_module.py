from PIL.Image import Image

from app.data.interfaces.visual_data import ObjectsData, VisualData
from app.machine_learning.object_detection.resnet_object_detection import (
    ResnetObjectDetection,
)
from app.processing.pipeline.base_module import VisualModule

detector = ResnetObjectDetection()


class ObjectsModule(VisualModule):
    def process(self, data: VisualData, image: Image) -> ObjectsData:
        objects = detector.detect_objects(image)

        return ObjectsData(
            **data.model_dump(),
            objects=objects,
        )

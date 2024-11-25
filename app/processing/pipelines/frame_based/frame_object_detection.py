from PIL.Image import Image

from app.data.interfaces.visual_information import TextSummaryVisualInformation, \
    ObjectsVisualInformation
from app.machine_learning.object_detection.ResnetObjectDetection import \
    ResnetObjectDetection

detector = ResnetObjectDetection()


def frame_object_detection(
    visual_info: TextSummaryVisualInformation,
    pil_image: Image
) -> ObjectsVisualInformation:
    objects = detector.detect_objects(pil_image)

    return ObjectsVisualInformation(
        **visual_info.model_dump(),
        objects=objects
    )

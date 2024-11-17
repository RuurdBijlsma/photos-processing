from PIL.Image import Image

from app.data.interfaces.visual_information import OCRVisualInformation, \
    FacesVisualInformation
from app.machine_learning.facial_recognition.InsightFacialRecognition import \
    InsightFacialRecognition

facial_recognition = InsightFacialRecognition()


def frame_faces(
    visual_info: OCRVisualInformation,
    pil_image: Image
) -> FacesVisualInformation:
    faces = facial_recognition.get_faces(pil_image)

    return FacesVisualInformation(
        **visual_info.model_dump(),
        faces=faces
    )

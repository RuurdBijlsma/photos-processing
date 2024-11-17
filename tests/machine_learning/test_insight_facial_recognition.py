from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial.distance import cosine

from app import \
    InsightFacialRecognition


def test_insight_facial_detection(tests_folder: Path) -> None:
    image = Image.open(tests_folder / "assets/faces.webp")
    facial_recognition = InsightFacialRecognition()

    faces = facial_recognition.get_faces(image)

    assert len(faces) == 15


def test_insight_facial_recognition(tests_folder: Path) -> None:
    img_1_a = Image.open(tests_folder / "assets/face1_a.jpg")
    img_1_b = Image.open(tests_folder / "assets/face1_b.jpg")
    img_2_a = Image.open(tests_folder / "assets/face2_a.jpg")
    img_2_b = Image.open(tests_folder / "assets/face2_b.jpg")
    facial_recognition = InsightFacialRecognition()

    face1_a = facial_recognition.get_faces(img_1_a)[0]
    face1_b = facial_recognition.get_faces(img_1_b)[0]
    face2_a = facial_recognition.get_faces(img_2_a)[0]
    face2_b = facial_recognition.get_faces(img_2_b)[0]

    walter = [face1_a, face1_b]
    micheal = [face2_a, face2_b]

    faces = [face1_a, face1_b, face2_a, face2_b]
    for face in faces:
        other_faces = [f for f in faces if f != face]
        distances = [
            cosine(face.embedding, other_face.embedding) for other_face in other_faces
        ]
        min_index = np.argmin(distances)
        closest_face = other_faces[min_index]
        if face in walter:
            assert closest_face in walter
        elif face in micheal:
            assert closest_face in micheal

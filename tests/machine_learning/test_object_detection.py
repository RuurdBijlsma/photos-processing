from pathlib import Path

import PIL
import pytest

from app.machine_learning.object_detection.resnet_object_detection import (
    ResnetObjectDetection,
)
from app.machine_learning.utils import draw_bounding_box


@pytest.mark.parametrize(("image", "objects"), [
    ("cat.jpg", ["cat"]),
    ("cluster.jpg", ["laptop"]),
])
def test_resnet_object_detection(
    assets_folder: Path,
    image: str,
    objects: list[str],
) -> None:
    detector = ResnetObjectDetection()
    pil_image = PIL.Image.open(assets_folder / image)
    detections = detector.detect_objects(pil_image)

    for i, object_box in enumerate(detections):
        draw_bounding_box(
            object_box,
            pil_image,
            f"test_img_out/{image}_{object_box.label}_out_{i}.jpg",
        )

    for target in objects:
        assert target in (obj.label for obj in detections)

from collections.abc import Sequence
from pathlib import Path

import cv2
import numpy as np
from PIL.Image import Image

from app.data.interfaces.ml_types import BaseBoundingBox


def coordinate_to_proportional(
    coordinate: Sequence[float | int], image: Image,
) -> tuple[float, float]:
    return coordinate[0] / image.width, coordinate[1] / image.height


def draw_bounding_box(
    box: BaseBoundingBox,
    pil_image: Image,
    out_path: str | Path,
) -> None:
    image_np = np.array(pil_image)
    image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    # Get image dimensions
    img_width, img_height = pil_image.size

    # Calculate bounding box coordinates in pixels
    box_x, box_y = box.position
    box_width = box.width
    box_height = box.height
    top_left = (int(box_x * img_width),
                int(box_y * img_height))
    bottom_right = (int((box_x + box_width) * img_width),
                    int((box_y + box_height) * img_height))

    # Draw rectangle and label
    color = (0, 255, 0)  # Green bounding box
    cv2.rectangle(image_cv2, top_left, bottom_right, color, thickness=2)

    cv2.imwrite(str(out_path), image_cv2)

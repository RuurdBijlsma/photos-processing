from PIL.Image import Image

from app.data.interfaces.ml_types import Coordinate


def coordinate_to_proportional(
    coordinate: list[float | int], image: Image
) -> Coordinate:
    return Coordinate(x=coordinate[0] / image.width, y=coordinate[1] / image.height)

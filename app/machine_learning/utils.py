from PIL.Image import Image


def coordinate_to_proportional(
    coordinate: list[float | int], image: Image
) -> tuple[float, float]:
    return coordinate[0] / image.width, coordinate[1] / image.height

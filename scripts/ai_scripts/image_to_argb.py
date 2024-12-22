import time

import PIL
import numpy as np
from PIL.Image import Image


def image_to_argb_int32(img: Image)->np.ndarray:
    # Open the image
    img = img.convert("RGBA")
    img.thumbnail((128, 128))

    # Extract channels: Alpha, Red, Green, Blue
    rgba_array = np.array(img)
    alpha = rgba_array[:, :, 3].astype(np.uint32) << 24
    red = rgba_array[:, :, 0].astype(np.uint32) << 16
    green = rgba_array[:, :, 1].astype(np.uint32) << 8
    blue = rgba_array[:, :, 2].astype(np.uint32)

    # Combine into ARGB format
    return alpha | red | green | blue


start = time.perf_counter_ns()

# Example usage
image_path = "../imgs/whimsical.png"  # Replace with your image path
image = PIL.Image.open(image_path)
argb_values = image_to_argb_int32(image)

print(f"time={(time.perf_counter_ns() - start)/1000000} ms")

print(argb_values)  # ARGB values as a 2D NumPy array

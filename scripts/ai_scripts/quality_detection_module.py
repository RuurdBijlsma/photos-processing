import os
import shutil
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt
import PIL.Image


def sharpness_measurement(image: npt.NDArray[np.uint8]) -> float:
    """
    Measure image sharpness using Laplacian variance method.
    A higher variance indicates a sharper image.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
    return laplacian.var()


def exposure_measurement(image: npt.NDArray[np.uint8]) -> tuple[float, float]:
    """
    Measure image exposure by analyzing brightness and contrast.
    - Check mean brightness (underexposed if too dark, overexposed if too bright).
    - Check contrast (low contrast may indicate poor exposure).
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray_image)
    # Calculate contrast (standard deviation of pixel intensities)
    contrast = np.std(gray_image)
    return float(mean_brightness), float(contrast)


def noise_measurement(image: npt.NDArray[np.uint8]) -> int:
    """
    Detect noise in an image by comparing the original image with a blurred version.
    - Higher differences between the original and blurred image indicate more noise.
    """

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    diff = cv2.absdiff(gray_image, blurred_image)
    return np.sum(diff)


def calculate_dynamic_range(image: np.ndarray, sample_fraction: float = 0.1) -> float:
    """Calculate the dynamic range of an image using a sample of the darkest and brightest pixels."""
    # Convert to grayscale if the image is in color
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Flatten the image into a 1D array and sort the pixel values
    flattened = image.flatten()
    sorted_pixels = np.sort(flattened)

    # Determine the number of pixels to sample
    num_pixels = len(sorted_pixels)
    sample_size = max(1, int(num_pixels * sample_fraction))  # Ensure at least 1 pixel is sampled

    # Get the mean of the darkest and brightest pixel samples
    darkest_mean = np.mean(sorted_pixels[:sample_size])
    brightest_mean = np.mean(sorted_pixels[-sample_size:])

    return brightest_mean - darkest_mean


def measure_clipping(image: np.ndarray) -> float:
    """
    Calculate the percentage of pixels that are clipped (either 0 or 255) in a grayscale image.
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Count the number of clipped pixels (0 or 255)
    total_pixels = image.size
    clipped_black = 0
    clipped_white = 255
    clipped_pixels = np.sum((image == clipped_black) | (image == clipped_white))

    # Calculate the percentage of clipped pixels
    return clipped_pixels / total_pixels


def compute_quality_score(
    image: npt.NDArray[np.uint8],
    sharpness_weight: float = 0.6,
    exposure_weight: float = 0.4,
    noise_weight: float = 0.1,
) -> float:
    """
    Calculate a composite quality score from 0 to 1 based on sharpness, exposure, and noise.
    A higher score indicates a better-quality image.
    """
    # 1. Sharpness: Normalize sharpness value
    sharpness = sharpness_measurement(image)
    sharpness_normalized = min(
        sharpness / 2000,
        1,
    )

    # 2. Exposure: Normalize brightness and contrast
    mean_brightness, contrast = exposure_measurement(image)
    # Calculate brightness score (80 is best, 0 and 160 worst)
    brightness_score = 1 - abs(mean_brightness - 160) / 160
    contrast_normalized = min(contrast / 90, 1)
    exposure_normalized = (brightness_score + contrast_normalized) / 2

    # 3. Noise: Normalize noise level (lower noise is better)
    noise_level = noise_measurement(image)
    noise_normalized = max(0, 1 - (noise_level / 150000000))

    # 4. Calculate composite score
    return (
        (sharpness_normalized * sharpness_weight)
        + (exposure_normalized * exposure_weight)
        + (noise_normalized * noise_weight)
    )


def composite_quality_score(
    image: npt.NDArray[np.uint8],
    sharpness_weight: float = 2.0,
    exposure_weight: float = 1.0,
    noise_weight: float = 0.2,
    dynamic_range_weight: float = 1.0,
    clipping_weight: float = 1.0,
) -> float:
    """
    Combine individual image quality metrics (sharpness, exposure, noise, dynamic range, clipping)
    into a single composite score from 0 to 1. Higher score indicates better image quality.
    Each score is weighted according to the specified weights.
    """
    # Measure sharpness (higher is better)
    sharpness = sharpness_measurement(image)
    sharpness_score = min(sharpness / 2000.0, 1.0)

    # Measure exposure
    mean_brightness, contrast = exposure_measurement(image)
    brightness_score = 1 - min(abs(mean_brightness - 160) / 160, 1)  # (non-extreme brightness is better)
    contrast_score = min(contrast / 100, 1.0)  # Higher contrast is better

    # Measure noise (lower noise is better)
    noise = noise_measurement(image)
    noise_score = max(1 - min(noise / 200000000.0, 1.0), 0.0)

    # Measure dynamic range (higher is better)
    dynamic_range = calculate_dynamic_range(image)
    dynamic_range_score = min(dynamic_range / 100, 1.0)  # Normalize dynamic range score

    # Measure clipping (lower is better)
    clipping_percentage = measure_clipping(image)
    clipping_score = max(1 - clipping_percentage / 0.1, 0.0)

    # Compute weighted composite score
    weighted_score = (
        sharpness_weight * sharpness_score
        + exposure_weight * (brightness_score + contrast_score) / 2
        + noise_weight * noise_score
        + dynamic_range_weight * dynamic_range_score
        + clipping_weight * clipping_score
    )

    # Normalize the final score to be between 0 and 1 by dividing by the total weight
    total_weight = sharpness_weight + exposure_weight + noise_weight + dynamic_range_weight + clipping_weight
    return weighted_score / total_weight


def process_images(input_folder: str, output_folder: str):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all image files in the input folder
    for file_path in Path(input_folder).glob("*.*"):
        try:
            # Load the image as PIL
            pil_image = PIL.Image.open(file_path)

            # Convert to OpenCV format
            image_cv2 = np.array(pil_image)
            if image_cv2.ndim == 3:  # Convert RGB to BGR for OpenCV
                image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_RGB2BGR)

            # sharpness_score = sharpness_measurement(image_cv2)
            # mean_brightness, contrast = exposure_measurement(image_cv2)
            # noise_score = noise_measurement(image_cv2)

            # Create a new file name with the dominant angle
            new_file_name = f"{composite_quality_score(image_cv2)*100}{file_path.suffix}"

            # Move the original file to the output folder with the new name
            shutil.copy(str(file_path), os.path.join(output_folder, new_file_name))
            print(f"Processed and moved: {file_path} -> {new_file_name}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")


# Example usage
input_folder = Path("../../media/images/1")
output_folder = Path("../../test_img_out")
process_images(str(input_folder), str(output_folder))

# class QualityDetectionModule(VisualModule):
#     def process(self, data: VisualData, image: Image) -> OCRData:
#         return OCRData(
#             **data.model_dump(),
#             has_legible_text=has_text,
#             ocr_text=extracted_text,
#             document_summary=summary,
#             ocr_boxes=boxes,
#         )

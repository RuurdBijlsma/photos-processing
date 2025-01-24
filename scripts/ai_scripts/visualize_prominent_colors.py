import os
from pathlib import Path

from PIL import Image, ImageDraw
from material_color_utilities import prominent_colors_from_image


def visualize_colors_on_images(input_dir: Path, output_dir: Path):
    """
    Visualizes 3 prominent colors on each image in the input directory by drawing circles
    and saves the result to the output directory.

    Args:
        input_dir: Directory containing input images.
        output_dir: Directory where output images will be saved.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)

        # Only process image files
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            continue

        try:
            # Open image
            image = Image.open(input_path).convert("RGB")
            width, height = image.size

            # Get prominent colors
            colors = prominent_colors_from_image(image)

            # Draw circles
            draw = ImageDraw.Draw(image)
            circle_radius = min(width, height) // 15  # Circle radius relative to image size
            spacing = circle_radius * 1.5  # Spacing between circles

            for i, color in enumerate(colors):
                center = (int(spacing * (i + 1)), circle_radius)
                draw.ellipse([
                    (center[0] - circle_radius, center[1] - circle_radius),
                    (center[0] + circle_radius, center[1] + circle_radius)
                ], fill=color, outline=(0, 0, 0))

            # Save the result
            output_path = os.path.join(output_dir, filename)
            image.save(output_path)
            print(f"Processed and saved: {output_path}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")


# Example usage:
# visualize_colors_on_images("/path/to/input_dir", "/path/to/output_dir")
input_folder = Path(__file__).parents[2] / "media/images/1"
output_folder = Path(__file__).parents[1] / "test_img_out"
visualize_colors_on_images(input_folder, output_folder)

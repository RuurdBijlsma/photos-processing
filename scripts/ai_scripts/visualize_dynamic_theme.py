from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from material_color_utilities import theme_from_image, DynamicScheme, prominent_colors_from_image, theme_from_color
import PIL.Image


def visualize_theme(
    theme: DynamicScheme,
    background_image: PIL.Image.Image,
    out_path: Path
):
    """Visualizes the most important parts of a material theme with a background image.

    Args:
        theme (DynamicScheme): An instance of DynamicScheme with color attributes as hex strings.
        background_image (PIL.Image.Image): The image to use as a background.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Convert the PIL image to a format compatible with matplotlib
    image_array = background_image.resize((800, 600))
    ax.imshow(image_array, extent=[0, 1, 0, 1], aspect='auto', interpolation='bilinear', alpha=1.0)
    # Semi-transparent overlay to simulate surface container color
    # overlay_rect = patches.Rectangle(
    #     (0, 0), 1, 1,
    #     color=theme.surface_container,
    #     alpha=0.8
    # )
    # ax.add_patch(overlay_rect)

    # Card
    card_rect = patches.FancyBboxPatch(
        (0.2, 0.4), 0.6, 0.4,
        boxstyle="round,pad=0.1",
        facecolor=theme.surface_container_high,
        edgecolor=theme.outline,
        linewidth=1.5
    )
    ax.add_patch(card_rect)

    # Title text
    ax.text(
        0.5, 0.7, "Title",
        ha="center", va="center",
        fontsize=16, weight="bold",
        color=theme.on_surface
    )

    # Content text
    ax.text(
        0.5, 0.55, "Content goes here",
        ha="center", va="center",
        fontsize=12,
        color=theme.on_surface_variant
    )

    # Button
    button_rect = patches.FancyBboxPatch(
        (0.4, 0.2), 0.2, 0.1,
        boxstyle="round,pad=0.1",
        facecolor=theme.primary,
        edgecolor=theme.outline,
        linewidth=1.5
    )
    ax.add_patch(button_rect)
    ax.text(
        0.5, 0.25, "Button",
        ha="center", va="center",
        fontsize=10, weight="bold",
        color=theme.on_primary
    )

    # Adjust axes and show
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # plt.show()
    plt.savefig(out_path)


image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
images_folder = Path(__file__).parents[1] / "imgs"
out_folder = Path(__file__).parents[1] / "test_img_out"
for image_path in images_folder.iterdir():
    if image_path.suffix.lower() not in image_extensions:
        continue
    image = PIL.Image.open(image_path)
    colors = prominent_colors_from_image(image)
    for color in colors:
        visualize_theme(
            (theme_from_color(color)).schemes.dark,
            image,
            out_folder / image_path.name
        )

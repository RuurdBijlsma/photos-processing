import PIL.Image
from material_color_utilities import Theme, Variant, prominent_colors_from_image

image = PIL.Image.open("../imgs/faces.jpg")
theme = Theme.from_source_color("#fd3", 3, Variant.EXPRESSIVE)
print(theme)

colors = prominent_colors_from_image(image)
print(colors)

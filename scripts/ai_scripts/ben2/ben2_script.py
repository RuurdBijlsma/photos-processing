from pathlib import Path

import BEN2
import torch
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

image_paths = list((Path(__file__).parents[2] / "imgs/clip_test_images").iterdir())
images = [Image.open(x) for x in image_paths]

model = BEN2.BEN_Base().to(device).eval() #init pipeline

# get BEN2_Base.pth from https://huggingface.co/PramaLLC/BEN2
model.loadcheckpoints("./BEN2_Base.pth")
foregrounds = [model.inference(image, refine_foreground=True) for image in images]
#Refine foreground is an extract postprocessing
# step that increases inference time but can
# improve matting edges. The default value is False.

for foreground, img_path in zip(foregrounds, image_paths):
    foreground.save(f"./{img_path.name}_foreground.png")

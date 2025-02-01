import BEN2
import torch
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

file = "../../imgs/motion.jpg"  # input image

model = BEN2.BEN_Base().to(device).eval() #init pipeline

# get BEN2_Base.pth from https://huggingface.co/PramaLLC/BEN2
model.loadcheckpoints("./BEN2_Base.pth")
image = Image.open(file)
foreground = model.inference(image, refine_foreground=False) #Refine foreground is an extract postprocessing step that increases inference time but can improve matting edges. The default value is False.

foreground.save("./foreground.png")

import torch
from diffusers import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16
)
pipeline.to("cuda")
pipeline(
    "An image of a girl posing before two bicycles on a path crossing a grass field. there are two houses in the background."
).images[0].show()

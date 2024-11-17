import PIL
import torch
from diffusers import (
    StableDiffusionInstructPix2PixPipeline,
    EulerAncestralDiscreteScheduler,
)

model_id = "timbrooks/instruct-pix2pix"
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16, safety_checker=None
)
pipe.to("cuda")
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

img_path = "media/images/1/20150714_170022.jpg"


def download_image(img_path):
    image = PIL.Image.open(img_path)
    image = PIL.ImageOps.exif_transpose(image)
    img_width = 1280
    image = image.resize((img_width, int(img_width * (image.height / image.width))))
    image = image.convert("RGB")
    return image


image = download_image(img_path)

while True:
    # prompt = "make her bike pink"
    images = pipe(
        input("Image prompt: "),
        image=image,
        num_inference_steps=50,
        image_guidance_scale=1,
    ).images
    images[0].show()

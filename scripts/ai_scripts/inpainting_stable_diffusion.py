import torch
from PIL import Image
from diffusers import StableDiffusion3InpaintPipeline

# Load the inpainting model
model_id = "stabilityai/stable-diffusion-3.5-medium"
pipe = StableDiffusion3InpaintPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")  # Use "cpu" if no GPU is available

# Load your original image and mask
image = Image.open("../imgs/car.png").convert("RGB")
mask = Image.open("../imgs/car_mask.png").convert("L")  # Mask should be in grayscale

prompt = "make the car baby blue."
num_inference_steps = 50
guidance_scale = 7.5

# Perform inpainting
with torch.autocast("cuda"):
    result = pipe(
        prompt=prompt,
        image=image,
        mask_image=mask,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        width=image.width,
        height=image.height
    ).images[0]

# Save or display the inpainted image
result.save("inpaint_blue.png")

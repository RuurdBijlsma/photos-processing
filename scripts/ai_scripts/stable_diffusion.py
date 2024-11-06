from diffusers import StableDiffusion3Pipeline
import torch

# Load the Stable Diffusion 3.5 Medium model
model_id = "stabilityai/stable-diffusion-3.5-medium"

# Initialize the pipeline
pipe = StableDiffusion3Pipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")  # Use "cpu" if you don’t have a GPU
pipe.enable_attention_slicing()

# Generate an image
prompt = "A serene mountain landscape at sunrise"
with torch.autocast("cuda"):
    image = pipe(
        prompt=prompt,
        num_inference_steps=30,
        guidance_scale=8,
        width=400,
        height=300,
    ).images[0]

# Save or display the image
image.save("output.png")

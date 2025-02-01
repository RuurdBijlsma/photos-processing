from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Load the model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load and preprocess the image
image_paths = list((Path(__file__).parents[2] / "imgs/clip_test_images").iterdir())
text = "A beach with pebbles."

images = [Image.open(x) for x in image_paths]
inputs_images = processor(
    images=images,
    return_tensors="pt",
    padding=True
)
inputs_text = processor(text=[text], return_tensors="pt", padding=True)

with torch.no_grad():
    image_embeddings = model.get_image_features(**inputs_images)
    text_embedding = model.get_text_features(**inputs_text)

image_embeddings = F.normalize(image_embeddings, dim=-1)
text_embedding = F.normalize(text_embedding, dim=-1)

similarities = (image_embeddings @ text_embedding.T).squeeze(1)

print(f"Similarity compared to '{text}':")
for image_path, score in zip(image_paths, similarities):
    print(f"\t{image_path.name}: {score.item():.2f}")

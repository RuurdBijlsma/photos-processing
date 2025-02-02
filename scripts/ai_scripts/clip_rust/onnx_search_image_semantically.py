from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image

from ai_scripts.clip_rust.onnx_image_compare import encode_images
from ai_scripts.clip_rust.onnx_text_compare import encode_texts

# Load and preprocess the image
image_paths = list((Path(__file__).parents[2] / "imgs/clip_test_images").iterdir())
images = [Image.open(x) for x in image_paths]
text = "A beach with pebbles."

text_embeds = encode_texts([text])
images_embeds = encode_images(images)

text_embeddings = torch.from_numpy(text_embeds).float()
image_embeddings = torch.from_numpy(images_embeds).float()

text_embeddings = F.normalize(text_embeddings, dim=-1)
image_embeddings = F.normalize(image_embeddings, dim=-1)

similarities = (image_embeddings @ text_embeddings.T).squeeze(1)

print(f"Similarity compared to '{text}':")
for image_path, score in zip(image_paths, similarities):
    print(f"\t{image_path.name}: {score.item():.2f}")

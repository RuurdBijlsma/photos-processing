from transformers import AutoProcessor, AutoModel

import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Load the model and processor
model = CLIPModel.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
processor = CLIPProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
# model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
# processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load and preprocess the image
grass_img = Image.open("../../media/images/1/20150716_164721.jpg")
keeb_img = Image.open("../../media/images/1/IMG_20120207_200437.jpg")
paper_img = Image.open("../../media/images/1/IMG_20120619_093127.jpg")
inputs_images = processor(
    images=[grass_img, keeb_img, paper_img], return_tensors="pt", padding=True
)

text = "grassy hill"
inputs_text = processor(text=[text], return_tensors="pt", padding=True)

# Generate embeddings
with torch.no_grad():
    # Generate image embeddings
    image_embeddings = model.get_image_features(**inputs_images)
    # Generate text embedding
    text_embedding = model.get_text_features(**inputs_text)

# Normalize embeddings for cosine similarity
image_embeddings = F.normalize(image_embeddings, p=2, dim=-1)
text_embedding = F.normalize(text_embedding, p=2, dim=-1)

# Calculate cosine similarities between text and each image
similarities = (image_embeddings @ text_embedding.T).squeeze(1)  # Shape: (3,)

# Display the similarity scores
for i, score in enumerate(similarities):
    print(f"Similarity between text and image {i + 1}: {score.item()}")

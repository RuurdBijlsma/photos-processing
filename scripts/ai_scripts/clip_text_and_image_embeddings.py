import torch
from PIL import Image
from torch.nn.functional import cosine_similarity
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load and preprocess the image
image = Image.open("media/images/1/20180812_150015.jpg")
image_inputs = processor(images=image, return_tensors="pt")
text_inputs = processor(
    text="a pita with gyros in it", return_tensors="pt", padding=True, truncation=True
)

# Get the image embedding
with torch.no_grad():
    image_embedding = model.get_image_features(**image_inputs)
    text_embedding = model.get_text_features(**text_inputs)

text_embedding = text_embedding / text_embedding.norm(dim=-1, keepdim=True)

similarity_score = cosine_similarity(text_embedding, image_embedding)
print(similarity_score)

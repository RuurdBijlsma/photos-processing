import torch
from PIL import Image
from torch.nn.functional import cosine_similarity
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load and preprocess the image
image = Image.open("../imgs/kampvuur.jpg")
image_inputs = processor(images=image, return_tensors="pt")
text_input1 = processor(
    text="a pita with gyros in it", return_tensors="pt", padding=True, truncation=True
)
text_input2 = processor(
    text="a campfire", return_tensors="pt", padding=True, truncation=True
)


# Get the image embedding
with torch.no_grad():
    image_embedding = model.get_image_features(**image_inputs)
    text_embedding1 = model.get_text_features(**text_input1)
    text_embedding2 = model.get_text_features(**text_input2)

text_embedding1 = text_embedding1 / text_embedding1.norm(dim=-1, keepdim=True)
text_embedding2 = text_embedding2 / text_embedding2.norm(dim=-1, keepdim=True)

similarity_score1 = cosine_similarity(text_embedding1, image_embedding)
similarity_score2 = cosine_similarity(text_embedding2, image_embedding)
print(similarity_score1)
print(similarity_score2)
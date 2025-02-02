import torch
from PIL import Image
from torch.nn.functional import cosine_similarity
from transformers import CLIPProcessor, CLIPModel

# Load the model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load and preprocess the image
input_names = [
    "beach_rocks.jpg",
    "beetle_car.jpg",
    "cat_face.jpg",
    "dark_sunset.jpg",
    "palace.jpg",
    "rocky_coast.jpg",
    "stacked_plates.jpg",
    "verdant_cliff.jpg",
]
images = [
    Image.open("../../imgs/clip_test_images/" + filename).convert("RGB")
    for filename in input_names
]

inputs_images = processor(
    images=images, return_tensors="pt", padding=True
)

with torch.no_grad():
    image_embeddings = model.get_image_features(**inputs_images)

image_embeddings = image_embeddings / image_embeddings.norm(dim=-1, keepdim=True)
query_embedding = image_embeddings[0, :].reshape((1, -1))
print(query_embedding[0,0:5])
similarities = cosine_similarity(query_embedding, image_embeddings[1:, :])

print(f"Query: {input_names[0]}")
for similarity, other_image in zip(similarities, input_names[1:]):
    print(f"\tSimilarity to {other_image}: {similarity:.2f}")

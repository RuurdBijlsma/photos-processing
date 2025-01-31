import torch
from torch.nn.functional import cosine_similarity
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

inputs = ["The weather outside is lovely.", "It's so sunny outside!", "She drove to the stadium."]
# Load and preprocess the image
text_inputs = processor(
    text=inputs, return_tensors="pt", padding=True, truncation=True
)

# Get the image embedding
with torch.no_grad():
    text_embeddings = model.get_text_features(**text_inputs)

# text_embeddings = text_embeddings / text_embeddings.norm(dim=-1, keepdim=True)

query_embedding = text_embeddings[0, :].reshape((1, -1))
similarities = cosine_similarity(query_embedding, text_embeddings[1:, :])

print(f"Query: {inputs[0]}")
for similarity, other_text in zip(similarities, inputs[1:]):
    print(f"Similarity to {other_text}: {similarity:.2f}")

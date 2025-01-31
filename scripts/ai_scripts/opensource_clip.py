import torch
import open_clip
from PIL import Image

# Load OpenCLIP model (ViT-H/14) with LAION-2B weights
model, _, preprocess = open_clip.create_model_and_transforms(
    model_name="ViT-H-14",
    pretrained="laion2b_s32b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-H-14")

# Move to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)


# Load and preprocess images
def load_images(image_paths):
    return [Image.open(path) for path in image_paths]


image_paths = [
    "../../media/images/1/20150731_155136.jpg",# auto
    "../../media/images/1/20170729_211259.jpg",# wrap
    "../../media/images/1/20180608_110630.jpg"# cat
]

images = load_images(image_paths)
processed_images = torch.stack([preprocess(img) for img in images]).to(device)

# Process text query
text_queries = ["car", "wrap", "cat"]  # Can handle multiple queries
tokenized_text = tokenizer(text_queries).to(device)

# Generate embeddings
with torch.no_grad(), torch.cuda.amp.autocast():
    image_features = model.encode_image(processed_images)
    text_features = model.encode_text(tokenized_text)

# Normalize features
image_features /= image_features.norm(dim=-1, keepdim=True)
text_features /= text_features.norm(dim=-1, keepdim=True)

# Calculate similarity (matrix product = cosine similarity)
similarities = (image_features @ text_features.T).cpu().numpy()

# Display results
for i, (score, img_path) in enumerate(zip(similarities, image_paths)):
    print(f"Image {i + 1} ({img_path.split('/')[-1]}):")
    for j, query in enumerate(text_queries):
        print(f"  Similarity with '{text_queries[j]}': {score[j]:.4f}")
    print()
from transformers import CLIPVisionModel
from datasets import load_dataset
import torch
import torchvision.transforms as T
import numpy as np
from tqdm import tqdm

# Load the model
model_name = "tanganke/clip-vit-large-patch14_sun397"
model = CLIPVisionModel.from_pretrained(model_name)

# Define manual preprocessing for CLIP ViT models
preprocess = T.Compose(
    [
        T.Resize(224, interpolation=T.InterpolationMode.BICUBIC),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711],
        ),
    ]
)

# Load SUN397 dataset
dataset = load_dataset("tanganke/sun397", split="train")


def get_image_embedding(image):
    """Extract embedding for a given image with manual preprocessing."""
    image = preprocess(image).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        outputs = model(pixel_values=image)
    return outputs.pooler_output.squeeze().cpu().numpy()


# Process each image in the dataset to get embeddings
embeddings = []
labels = []

for item in tqdm(dataset):
    label = item["label"]  # Scene label

    # Compute embedding
    embedding = get_image_embedding(item["image"])
    embeddings.append(embedding)
    labels.append(label)

# Save embeddings and labels
np.save("sun397_embeddings.npy", np.array(embeddings))
np.save("sun397_labels.npy", np.array(labels))

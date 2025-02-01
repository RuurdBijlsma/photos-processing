import onnxruntime
import numpy as np
import torch
from PIL import Image
from torch.nn.functional import cosine_similarity

# Configuration from CLIP's processing
IMAGE_SIZE = 224
MEAN = np.array([0.48145466, 0.4578275, 0.40821073])[None, None, :]
STD = np.array([0.26862954, 0.26130258, 0.27577711])[None, None, :]


def preprocess_image(image):
    # Resize the shorter side to 224 while maintaining aspect ratio
    w, h = image.size
    target_size = 224

    # Determine which dimension is shorter and compute new size
    if w < h:
        new_w = target_size
        new_h = int(h * (target_size / w))
    else:
        new_h = target_size
        new_w = int(w * (target_size / h))

    # Resize using BICUBIC interpolation
    image = image.resize((new_w, new_h), resample=Image.BICUBIC)

    # Center crop to 224x224
    left = (new_w - target_size) // 2
    top = (new_h - target_size) // 2
    right = left + target_size
    bottom = top + target_size
    image = image.crop((left, top, right, bottom))

    # Normalize and transpose to CHW format
    arr = np.array(image).astype(np.float32) / 255.0
    arr = (arr - MEAN) / STD
    return np.transpose(arr, (2, 0, 1))[None, ...]


# Load ONNX model
ort_session = onnxruntime.InferenceSession("clip_vision.onnx")

# Load and preprocess images
input_names = ["campfire.jpg", "fire_basket.jpg", "market.jpg"]
images = [Image.open("../../imgs/" + filename).convert("RGB") for filename in input_names]

# Batch process images
pixel_values = np.concatenate([preprocess_image(img) for img in images], axis=0)

# Run inference with the corrected ONNX model
ort_inputs = {'pixel_values': pixel_values.astype(np.float32)}
ort_outputs = ort_session.run(None, ort_inputs)

# Directly use the normalized embeddings
image_embeddings = torch.from_numpy(ort_outputs[0])  # Now index 0

# Calculate similarities (same as before)
query_embedding = image_embeddings[0, :].reshape((1, -1))
print(query_embedding[0,0:5])
similarities = cosine_similarity(query_embedding, image_embeddings[1:, :])

print(f"Query: {input_names[0]}")
for similarity, other_image in zip(similarities, input_names[1:]):
    print(f"Similarity to {other_image}: {similarity:.2f}")

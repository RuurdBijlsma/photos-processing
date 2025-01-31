import onnxruntime
import torch
from torch.nn.functional import cosine_similarity
from transformers import CLIPProcessor, CLIPModel
import numpy as np

# Load processor and original model for projection weights
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
original_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

# Get the text projection matrix
text_projection = original_model.text_projection.weight.detach().numpy().T

# Load ONNX session
ort_session = onnxruntime.InferenceSession(
    "clip_text.onnx",
    providers=["CPUExecutionProvider"]  # Force FP32
)

# Process texts
inputs = [
    "The weather outside is lovely.",
    "It's so sunny outside!",
    "She drove to the stadium."
]

text_inputs = processor(
    text=inputs,
    return_tensors="pt",
    padding=True,
    truncation=True
)

# Run ONNX inference
ort_outputs = ort_session.run(
    None,
    {
        "input_ids": text_inputs["input_ids"].numpy(),
        "attention_mask": text_inputs["attention_mask"].numpy()
    }
)

# Get and project embeddings
pooler_output = ort_outputs[1]  # Shape: (batch_size, hidden_size)
text_embeddings = np.dot(pooler_output, text_projection)  # Apply projection
text_embeddings = torch.from_numpy(text_embeddings).float()

# Normalize exactly like original model
text_embeddings = text_embeddings / text_embeddings.norm(dim=-1, keepdim=True)

# Calculate similarities
query_embedding = text_embeddings[0].unsqueeze(0)
other_embeddings = text_embeddings[1:]

similarities = cosine_similarity(query_embedding, other_embeddings)

print(f"Query: {inputs[0]}")
for similarity, text in zip(similarities, inputs[1:]):
    print(f"Similarity to '{text}': {similarity.item():.2f}")

# Original model
with torch.no_grad():
    orig_outputs = original_model.text_model(**text_inputs)
orig_pooled = orig_outputs[1]
orig_projected = orig_pooled @ original_model.text_projection.weight.T
orig_normalized = orig_projected / orig_projected.norm(dim=-1, keepdim=True)

# ONNX outputs
onnx_projected = torch.from_numpy(np.dot(ort_outputs[1], text_projection))
onnx_normalized = onnx_projected / onnx_projected.norm(dim=-1, keepdim=True)

print("Max projection difference:", torch.max(torch.abs(orig_projected - onnx_projected)).item())
print("Max normalization difference:", torch.max(torch.abs(orig_normalized - onnx_normalized)).item())

# Compare raw pooler outputs (before projection)
orig_pooled = orig_outputs[1]  # From original PyTorch model
onnx_pooled = torch.from_numpy(ort_outputs[1]).float()  # From ONNX

print("\nPooler output comparison:")
print(f"Original shape: {orig_pooled.shape} | ONNX shape: {onnx_pooled.shape}")
print(f"Max absolute difference: {torch.max(torch.abs(orig_pooled - onnx_pooled)):.4f}")
print(f"Average difference: {torch.mean(torch.abs(orig_pooled - onnx_pooled)):.4f}")
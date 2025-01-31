# Install dependencies: pip install torch onnx transformers
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Load the model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Dummy inputs for tracing
text_inputs = processor(text=["This is a dummy text."], return_tensors="pt", padding=True)
image_inputs = processor(images=Image.new("RGB", (224, 224)), return_tensors="pt")

# Export text encoder
# Modified export code (should be re-run)
torch.onnx.export(
    model.text_model,
    (text_inputs["input_ids"], text_inputs["attention_mask"]),
    "clip_text.onnx",
    opset_version=14,
    input_names=["input_ids", "attention_mask"],
    output_names=["last_hidden_state", "pooler_output"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "last_hidden_state": {0: "batch_size", 1: "sequence_length"},
        "pooler_output": {0: "batch_size"}
    }
)
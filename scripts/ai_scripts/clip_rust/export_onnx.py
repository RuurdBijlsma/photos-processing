# Install dependencies: pip install torch onnx transformers Pillow
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Load the model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Create dummy inputs
# For text encoder
text_inputs = processor(text=["This is a dummy text."], return_tensors="pt", padding=True)

# For image encoder (create a dummy image)
dummy_image = Image.new("RGB", (224, 224), color="red")
image_inputs = processor(images=[dummy_image], return_tensors="pt", padding=True)

# Export text encoder
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

# Export image encoder
# Export wrapper combining vision_model + projection + normalization
class CLIPVisionWrapper(torch.nn.Module):
    def __init__(self, vision_model, visual_projection):
        super().__init__()
        self.vision_model = vision_model
        self.visual_projection = visual_projection

    def forward(self, pixel_values):
        # Forward through vision model
        vision_outputs = self.vision_model(pixel_values=pixel_values)
        pooled_output = vision_outputs[1]  # pooler_output

        # Project and normalize
        projected = self.visual_projection(pooled_output)
        normalized = torch.nn.functional.normalize(projected, dim=-1)
        return normalized

# Create the wrapped model
vision_wrapper = CLIPVisionWrapper(model.vision_model, model.visual_projection)

# Export with the wrapper
torch.onnx.export(
    vision_wrapper,
    image_inputs["pixel_values"],
    "clip_vision.onnx",
    opset_version=14,
    input_names=["pixel_values"],
    output_names=["image_embeddings"],
    dynamic_axes={
        "pixel_values": {0: "batch_size"},
        "image_embeddings": {0: "batch_size"}
    }
)

print("Exported both text and vision encoders to ONNX format!")
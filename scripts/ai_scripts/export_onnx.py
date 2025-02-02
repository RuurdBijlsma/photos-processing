import torch
from transformers import CLIPModel, CLIPProcessor

# Load the CLIP model and processor
model_name = "openai/clip-vit-large-patch14"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

# Extract the text encoder
text_encoder = model.text_model

# Example input for the text encoder
dummy_input = processor(text=["A sample text"], return_tensors="pt", padding=True)

class TextEncoderWithProjection(torch.nn.Module):
    def __init__(self, text_model, text_projection):
        super().__init__()
        self.text_model = text_model
        self.text_projection = text_projection

    def forward(self, input_ids, attention_mask):
        outputs = self.text_model(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output  # Already contains EOS embedding
        return self.text_projection(pooled_output)

# Export with projection
text_encoder_with_projection = TextEncoderWithProjection(
    model.text_model,
    model.text_projection
)

torch.onnx.export(
    text_encoder_with_projection,
    (dummy_input["input_ids"], dummy_input["attention_mask"]),
    "clip_text_encoder.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["text_embeddings"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "text_embeddings": {0: "batch_size"},
    },
    opset_version=20,
)
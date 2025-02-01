import onnxruntime
import numpy as np
import torch
from torch.nn.functional import cosine_similarity
from tokenizers import Tokenizer

# Load the tokenizer from tokenizer.json
tokenizer = Tokenizer.from_file("tokenizer.json")

# Load ONNX model
text_session = onnxruntime.InferenceSession(
    "clip_text.onnx",
    providers=["CPUExecutionProvider"]
)

# Input texts
texts = [
    "The weather outside is lovely.",
    "It's so sunny outside!",
    "She drove to the stadium."
]

# Tokenize texts using the tokenizer
max_length = 77  # CLIP models use a max sequence length of 77
encoded = tokenizer.encode_batch(texts)

# Convert tokenized output to numpy arrays
input_ids = np.zeros((len(texts), max_length), dtype=np.int64)
attention_mask = np.zeros((len(texts), max_length), dtype=np.int64)

for i, encoding in enumerate(encoded):
    tokens = encoding.ids[:max_length]  # Ensure max length
    input_ids[i, :len(tokens)] = tokens
    attention_mask[i, :len(tokens)] = 1  # Mask only valid tokens

# Run inference
text_embeds = text_session.run(
    None,
    {
        "input_ids": input_ids,
        "attention_mask": attention_mask
    }
)[0]

# Convert to tensor and calculate similarities
text_embeddings = torch.from_numpy(text_embeds).float()
similarities = cosine_similarity(text_embeddings[0:1], text_embeddings[1:])

print(f"Query: {texts[0]}")
for similarity, other_text in zip(similarities, texts[1:]):
    print(f"Similarity to '{other_text}': {similarity:.2f}")

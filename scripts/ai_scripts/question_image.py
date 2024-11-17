from pathlib import Path

import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained(
    "openbmb/MiniCPM-V-2", trust_remote_code=True, torch_dtype=torch.bfloat16
)
# For Nvidia GPUs support BF16 (like A100, H100, RTX3090)
# model = model.to(device='cuda', dtype=torch.bfloat16)
# For Nvidia GPUs do NOT support BF16 (like V100, T4, RTX2080)
model = model.to(device="cuda", dtype=torch.float16)
# For Mac with MPS (Apple silicon or AMD GPUs).
# Run with `PYTORCH_ENABLE_MPS_FALLBACK=1 python test.py`
# model = model.to(device='mps', dtype=torch.float16)

tokenizer = AutoTokenizer.from_pretrained("openbmb/MiniCPM-V-2", trust_remote_code=True)
model.eval()

img_url = Path("../../media/images/1/20170726_152057.jpg")
image = Image.open(img_url).convert("RGB")

questions = [
    "You are a scene recognition model trained on places 365. What is the scene in this image? Answer using at most 2 words.",
    "what search terms would you use to find this image? Answer with the terms only, separated by commas, give at least 3 terms.",
    "Perfectly describe this photo in detail, leave nothing out. The original image will be recreated from your response. Don't embellish your response just keep it factual.",
    "You are a photographer who's creating a selection of images to show to family. "
    "The selection should have high quality and interesting images that tell part of the story. "
    "Should this photo be included in the album? Indicate with a number from 1 (no) to 10 (absolutely). "
    "Only answer with the number",
    "Rate this photo on a scale of 1 to 10 in terms of professional quality standards? Only answer with the number.",
    "You are a activity recognition model. What is the activity displayed in this image? Answer using at most 2 words.",
    "You are a occasion and event recognition model. What is the occasion or event displayed in this image? e.g., birthday, vacation, graduation. Answer using at most 2 words.",
]
for question in questions:
    msgs = [{"role": "user", "content": question}]

    # Fix this model with this comment: https://huggingface.co/openbmb/MiniCPM-V-2/discussions/23
    res, context, _ = model.chat(
        image=image,
        msgs=msgs,
        context=None,
        tokenizer=tokenizer,
        sampling=True,
        temperature=0.7,
    )
    print(context[0]["content"])
    print()
    print(res)
    print()
    print(
        "=========================================================================================================="
    )
    print()

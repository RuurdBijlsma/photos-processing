from pathlib import Path

import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained('openbmb/MiniCPM-V-2', trust_remote_code=True, torch_dtype=torch.bfloat16)
# For Nvidia GPUs support BF16 (like A100, H100, RTX3090)
# model = model.to(device='cuda', dtype=torch.bfloat16)
# For Nvidia GPUs do NOT support BF16 (like V100, T4, RTX2080)
model = model.to(device='cuda', dtype=torch.float16)
# For Mac with MPS (Apple silicon or AMD GPUs).
# Run with `PYTORCH_ENABLE_MPS_FALLBACK=1 python test.py`
# model = model.to(device='mps', dtype=torch.float16)

tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-V-2', trust_remote_code=True)
model.eval()

img_url = Path('ocr.jpg')
image = Image.open(img_url).convert("RGB")

questions = [
    "You are an OCR bot, extract the text from this image.",  # werkt niet goed
    "what search terms would you use to find this image?",
    "Perfectly describe this photo in detail, leave nothing out. The original image will be recreated from your response.",
    "You are a photographer who's creating a selection of images to show to family. "
    "The selection should have high quality and interesting images that tell part of the story. "
    "Should this photo be included in the album? Indicate with a number from 1 (no) to 10 (absolutely).",
    "Rate this photo on a scale of 1 to 10 in terms of professional quality standards? Give the number only.",
    "Does this photo appear to be taken indoors or outdoors? If outdoors, can you recognize the location or "
    "type of place (e.g., park, beach, city)? Keep your answer short and confident.",
    "Does this image appear to be taken during the day or night? Can you estimate the time of day (morning, afternoon, evening)? Keep your answer short and confident.",
    "What kind of weather is visible in this photo? Does it indicate a specific season (e.g., winter, summer)? Keep your answer short and confident.",
    "What activity is happening in this photo? (e.g., walking, playing, working) Keep your answer short and confident.",
    "How many people are in this photo? Just give a number.",
    "What emotions are visible on the faces in this photo (e.g., happiness, surprise, sadness)? Keep your answer short and confident.",
    "Describe the clothing or fashion style of the person in this photo.",
    "What are the main objects visible in this photo? (e.g., dog, car, table)",
    "What are the dominant colors in this photo?",
    "How memorable is this image, on a scale from 1 to 10? Just give a number.",
    "If there is a person in this photo, how old are they? Give an exact integer number. If there isn't a person, respond with -1.",
    "Does this photo capture strong emotions or sentimental moments?",
    "What event or occasion does this image seem to represent? (e.g., birthday, vacation, celebration) Keep your answer short and confident.",
]
for question in questions:
    msgs = [
        {'role': "user", 'content': question}
    ]

    # Fix this model with this comment: https://huggingface.co/openbmb/MiniCPM-V-2/discussions/23
    res, context, _ = model.chat(
        image=image,
        msgs=msgs,
        context=None,
        tokenizer=tokenizer,
        sampling=True,
        temperature=0.7
    )
    print(context[0]["content"])
    print()
    print(res)
    print()
    print("==========================================================================================================")
    print()

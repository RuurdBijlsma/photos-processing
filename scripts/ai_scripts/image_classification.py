from pathlib import Path

from PIL import Image
from transformers import ViTImageProcessor, ViTForImageClassification

img_url = Path("../../media/images/1/IMG_20160927_121437.jpg")
image = Image.open(img_url)

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")

inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits
# model predicts one of the 1000 ImageNet classes
predicted_class_idx = logits.argmax(-1).item()
print("Predicted class:", model.config.id2label[predicted_class_idx])

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

model = AutoModelForImageClassification.from_pretrained(
    "miguelcarv/resnet-152-text-detector",
)

processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50", do_resize=False)

# image_path = "../../data/images/2/IMG_20171106_110319.jpg"
image_path = "../imgs/ocr.jpg"
image = Image.open(image_path).convert("RGB").resize((300, 300))
inputs = processor(image, return_tensors="pt").pixel_values

with torch.no_grad():
    outputs = model(inputs)

logits_per_image = outputs.logits
probs = logits_per_image.softmax(dim=1)
print(probs)
has_legible_text = probs[0][1] > probs[0][0]
if not has_legible_text:
    print("Image has no legible text!")
else:
    print("Image has legible text!")
    from unstructured.partition.image import partition_image

    # Returns a List[Element] present in the pages of the parsed image document
    elements = partition_image(image_path)

    out_txt = ""
    for element in elements:
        if hasattr(element, "text"):
            out_txt += element.text.strip() + "\n"

    print(out_txt)

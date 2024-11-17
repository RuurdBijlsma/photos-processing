from pathlib import Path

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large"
).to("cuda")

img_url = Path("./media/images/1/P_20230403_132322.jpg")
raw_image = Image.open(img_url).convert("RGB")

# conditional image captioning
input_texts = [
    ("this photo is taken in ", 5, 15),
    ("the subject of this photo is ", 5, 15),
    ("the weather here is ", 5, 15),
    ("the main action occurring in this image is ", 10, 25),
    ("the emotions conveyed in this picture are ", 5, 20),
    ("this image tells a story about ", 5, 20),
    ("one interesting detail in this photo is ", 5, 20),
    ("the significance of the setting in this image is ", 10, 30),
    ("this scene could be described as ", 5, 15),
    ("this image evokes a feeling of ", 5, 15),
    ("the colors in this image suggest ", 5, 15),
    ("this photo captures a moment of ", 5, 20),
    ("a viewer might wonder about ", 5, 20),
    ("the perspective shown in this image highlights ", 10, 25),
    ("the style of this photo reflects ", 5, 15),
    ("the mood of this scene is ", 5, 15),
    ("the landscape is ", 5, 15),
    ("this image was taken with a ", 5, 15),
    ("the geography can be described as ", 5, 15),
    ("the lighting in this photo creates ", 5, 20),
    ("the composition of this image features ", 5, 20),
    ("the cultural significance of this image is ", 10, 25),
    ("the mood created by the colors is ", 5, 15),
    ("the subject’s expression indicates ", 5, 20),
    ("this photo captures the essence of ", 5, 20),
    ("the focal point of this image is ", 5, 15),
    ("this image highlights the contrast between ", 10, 30),
    ("the texture seen in this image is ", 5, 15),
    ("the historical context of this scene is ", 10, 30),
    ("the main theme represented in this photo is ", 10, 25),
]

for text, min_length, max_length in input_texts:
    inputs = processor(raw_image, text, return_tensors="pt").to("cuda")

    out = model.generate(
        **inputs,
        min_length=min_length,
        max_length=max_length,
        num_beams=5,
    )
    print(processor.decode(out[0], skip_special_tokens=True))

# unconditional image captioning
# inputs = processor(raw_image, return_tensors="pt").to("cuda")
#
# out = model.generate(**inputs)
# print(processor.decode(out[0], skip_special_tokens=True))

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pytesseract import Output

image = Image.open("../imgs/ocr.jpg")
img = np.array(image)
if img.shape[2] == 3:  # Check if it's a color image
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

d = pytesseract.image_to_data(
    img, lang="+".join(["nld", "eng"]), output_type=Output.DICT
)
txt = pytesseract.image_to_string(
    img,
    lang="+".join(["nld", "eng"]),
)

# Loop through the detected boxes
n_boxes = len(d["level"])
for i in range(n_boxes):
    if d["conf"][i] < 0:
        continue
    text = d["text"][i]
    if text.strip() == "":
        continue

    (x, y, w, h) = (d["left"][i], d["top"][i], d["width"][i], d["height"][i])
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, i * 2), 2)
    text_position = (x, y - 5 if y > 10 else y + h + 15)
    cv2.putText(
        img,
        text,
        text_position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,  # Font scale
        (255, d["word_num"][i] * 70, 0),  # Font color (blue in this case)
        1,  # Font thickness
        cv2.LINE_AA,
    )

# Show the image with bounding boxes and text
cv2.imshow("img", img)
cv2.waitKey(0)

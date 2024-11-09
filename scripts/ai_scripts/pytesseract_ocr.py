import pytesseract
from PIL import Image


# Step 1: Use OCR to extract text from the image
def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


image_path = "../imgs/ocr.jpg"
extracted_text = extract_text_from_image(image_path)
print(extracted_text)

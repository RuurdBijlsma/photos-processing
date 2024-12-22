from pathlib import Path

from PIL import Image

from app.machine_learning.ocr.resnet_tesseract_ocr import ResnetTesseractOCR
from app.machine_learning.utils import draw_bounding_box


def test_resnet_tesseract_ocr_text(assets_folder: Path) -> None:
    image = Image.open(assets_folder / "ocr.jpg")
    ocr = ResnetTesseractOCR()
    has_text = ocr.has_legible_text(image)
    assert has_text

    extracted_text = ocr.get_text(image)
    assert "SPAGHETTI" in extracted_text.upper()


def test_resnet_tesseract_ocr_boxes(assets_folder: Path) -> None:
    image = Image.open(assets_folder / "ocr.jpg")
    ocr = ResnetTesseractOCR()

    boxes = ocr.get_boxes(image)
    for box in boxes:
        draw_bounding_box(box, image, f"test_img_out/{box.text}_out_ocr.jpg")
    required_boxes_amount = 50
    assert len(boxes) > required_boxes_amount
    found_spaghetti = False
    for box in boxes:
        if "SPAGHETTI" in box.text:
            found_spaghetti = True
            break
    assert found_spaghetti

from pathlib import Path

from PIL import Image

from photos.machine_learning.ocr.ResnetTesseractOCR import ResnetTesseractOCR


def test_resnet_tesseract_ocr_text(tests_folder: Path) -> None:
    image = Image.open(tests_folder / "assets/ocr.jpg")
    ocr = ResnetTesseractOCR()
    has_text = ocr.has_legible_text(image)
    assert has_text

    extracted_text = ocr.get_text(image)
    assert "SPAGHETTI" in extracted_text.upper()


def test_resnet_tesseract_ocr_boxes(tests_folder: Path) -> None:
    image = Image.open(tests_folder / "assets/ocr.jpg")
    ocr = ResnetTesseractOCR()

    boxes = ocr.get_boxes(image)
    assert len(boxes) > 50
    found_spaghetti = False
    for box in boxes:
        if "SPAGHETTI" in box.text:
            found_spaghetti = True
            break
    assert found_spaghetti

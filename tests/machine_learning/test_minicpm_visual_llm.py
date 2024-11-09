from pathlib import Path

from PIL import Image

from photos.machine_learning.visual_llm.MiniCPMVisualLLM import MiniCPMVisualLLM


def test_minicpm_visual_llm(tests_folder: Path) -> None:
    visual_llm = MiniCPMVisualLLM()
    image = Image.open(tests_folder / "assets/cat.jpg")
    response = visual_llm.image_question(image=image, question="What creature is laying on this bed?")
    print(response)

import os
from pathlib import Path

import pytest
from PIL import Image

from app.machine_learning.visual_llm.MiniCPMLLM import MiniCPMLLM
from app.machine_learning.visual_llm.OpenAILLM import OpenAILLM
from app.machine_learning.visual_llm.VisualLLMProtocol import ChatMessage, \
    VisualLLMProtocol


@pytest.mark.cuda
@pytest.mark.parametrize("visual_llm", [MiniCPMLLM(), OpenAILLM()])
def test_minicpm_visual_llm(tests_folder: Path, visual_llm: VisualLLMProtocol) -> None:
    if isinstance(visual_llm, OpenAILLM) and os.environ.get("OPENAI_API_KEY") == None:
        # Only run test if OPENAI_API_KEY is set.
        pytest.skip("OPENAI_API_KEY is not set, so OpenAILLM test is skipped.")
    image = Image.open(tests_folder / "assets/cat.jpg")
    answer = visual_llm.image_question(
        image=image, question="What creature is laying on this bed?"
    )
    assert "cat" in answer.lower()
    found_cat = False
    for message in visual_llm.stream_chat(
        ChatMessage(message="What creature is laying on this bed?", images=[image])
    ):
        if "cat" in message.lower():
            found_cat = True
    assert found_cat

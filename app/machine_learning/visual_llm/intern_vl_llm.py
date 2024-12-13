from functools import lru_cache
from threading import Thread
from typing import Generator, Any

import torch
import torchvision.transforms as T
from PIL.Image import Image
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoModel, AutoTokenizer, TextIteratorStreamer, PreTrainedModel

from app.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM, ChatMessage

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def build_transform(input_size):
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])
    return transform


def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio


def dynamic_preprocess(image, min_num=1, max_num=12, image_size=448,
                       use_thumbnail=False):
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in
        range(1, n + 1) if
        max_num >= i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images


def load_image(image: Image, input_size: int = 448, max_num: int = 12):
    image = image.convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(
        image,
        image_size=input_size,
        use_thumbnail=True,
        max_num=max_num
    )
    pixel_values = [transform(image) for image in images]
    return torch.stack(pixel_values)


@lru_cache
def get_model_etc() -> tuple[
    PreTrainedModel, AutoTokenizer, TextIteratorStreamer, dict[str, Any]
]:
    path = 'OpenGVLab/InternVL2_5-2B'
    model = AutoModel.from_pretrained(
        path,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
        use_flash_attn=True,
        trust_remote_code=True).eval().cuda()
    tokenizer = AutoTokenizer.from_pretrained(
        path,
        trust_remote_code=True,
        use_fast=False
    )
    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True,
        timeout=20
    )
    generation_config = {
        "max_new_tokens": 1024,
        "do_sample": False,
        "streamer": streamer
    }
    return model, tokenizer, streamer, generation_config


class InternVLLLM(BaseVisualLLM):
    def stream_chat(
        self,
        messages: list[ChatMessage],
        convert_images: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> Generator[str, None, None]:
        model, tokenizer, streamer, generation_config = get_model_etc()

        current_message = messages.pop()
        pixel_values = torch.cat([
            load_image(image).to(torch.bfloat16).cuda()
            for image in current_message.images
        ], dim=0)
        history = None if len(messages) == 0 else messages
        # Define the generation configuration
        # Start the model chat in a separate thread
        thread = Thread(
            target=model.chat,
            kwargs=dict(
                tokenizer=tokenizer,
                pixel_values=pixel_values,
                question=current_message.message,
                history=history,
                return_history=False,
                generation_config=generation_config,
            ))
        thread.start()
        for chunk in streamer:
            if chunk == model.conv_template.sep:
                break
            yield chunk

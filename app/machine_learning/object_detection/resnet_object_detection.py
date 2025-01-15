from functools import lru_cache

import torch
from PIL.Image import Image
from transformers import (
    DetrForObjectDetection,
    DetrImageProcessor,
    PreTrainedModel,
)

from app.data.interfaces.ml_types import ObjectBox
from app.machine_learning.object_detection.object_detection_protocol import (
    ObjectDetectionProtocol,
)
from app.machine_learning.utils import coordinate_to_proportional


@lru_cache
def get_model_and_processor() -> tuple[
    DetrImageProcessor, PreTrainedModel,
]:
    processor = DetrImageProcessor.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm",
    )
    model = DetrForObjectDetection.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm",
    )
    assert isinstance(processor, DetrImageProcessor)
    return processor, model


class ResnetObjectDetection(ObjectDetectionProtocol):

    def detect_objects(self, image: Image) -> list[ObjectBox]:
        # you can specify the revision tag if you don't want the timm dependency
        processor, model = get_model_and_processor()

        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)

        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(
            outputs,
            target_sizes=target_sizes,
            threshold=0.8,
        )[0]

        return [
            ObjectBox(
                confidence=score.item(),
                label=model.config.id2label[label.item()],
                position=coordinate_to_proportional(
                    (float(box[0].item()), float(box[1].item())),
                    image,
                ),
                width=(box[2].item() - box[0].item()) / image.width,
                height=(box[3].item() - box[1].item()) / image.height,
            )
            for score, label, box in
            zip(results["scores"], results["labels"], results["boxes"], strict=False)
        ]

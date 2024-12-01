import time
from abc import ABC, abstractmethod

from PIL.Image import Image

from app.data.interfaces.image_data import ImageData
from app.data.interfaces.visual_data import VisualData


class BaseModule(ABC):
    run_times: list[float]
    name: str

    def __init__(self):
        self.name = self.__class__.__name__
        self.run_times = []

    def base_run(self, func, *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        self.run_times.append(time.time() - start_time)
        return result


class ImageModule(BaseModule):
    def run(self, data: ImageData) -> ImageData:
        return self.base_run(self.process, data)

    @abstractmethod
    def process(self, data: ImageData) -> ImageData:
        pass


class VisualModule(BaseModule):
    def run(self, data: VisualData, image: Image) -> VisualData:
        return self.base_run(self.process, data, image)

    @abstractmethod
    def process(self, data: VisualData, image: Image) -> VisualData:
        pass

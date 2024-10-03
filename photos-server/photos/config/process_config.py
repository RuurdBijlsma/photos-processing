from pathlib import Path

from pydantic_settings import BaseSettings


class ProcessConfig(BaseSettings):
    thumbnails_dir: Path = Path("../data/thumbnails")
    thumbnail_sizes: list[int] = [240, 480, 1080]
    image_suffixes: tuple[str, ...] = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".gif",
        ".tiff",
        ".webp",
    )


process_config = ProcessConfig()

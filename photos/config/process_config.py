from pathlib import Path

from pydantic_settings import BaseSettings


class ProcessConfig(BaseSettings):
    thumbnails_dir: Path = Path("data/thumbnails")
    thumbnail_sizes: list[int] = [240, 480, 1080]
    web_video_height: int = 1080
    image_suffixes: tuple[str, ...] = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".gif",
        ".tiff",
        ".webp",
    )
    video_suffixes: tuple[str, ...] = (".mp4", ".mkv", ".webm")

    @property
    def media_suffixes(self) -> tuple[str, ...]:
        return self.image_suffixes + self.video_suffixes


process_config = ProcessConfig()

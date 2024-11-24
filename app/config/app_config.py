from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from app.config.config_types import LLMProvider


class AppConfig(BaseSettings):
    password_secret: str = (
        "3df8944bf8afe568d4f0011db0d7fe1ef724f12227b6254116d128caf8c3bee5"
    )

    debug: bool = True
    host_thumbnails: bool = True
    multithreaded_processing: bool = False
    connection_string: str = (
        "postgresql+asyncpg://postgres:flyingsquirrel@localhost/photos"
    )
    media_languages: list[str] = ["nld", "eng"]
    enable_llm: bool = False
    llm_provider: LLMProvider = LLMProvider.MINICPM

    document_detection_threshold: int = Field(
        default=65,
        description="How many characters should be recognized before classifying "
                    "it as a document and making a summary."
    )
    face_detection_threshold: float = Field(
        default=0.7,
        description="The minimum confidence threshold for detecting a face. "
                    "Values should be between 0 and 1. Higher values mean higher "
                    "confidence in the detection."
    )
    images_dir: Path = Path("media/images")
    thumbnails_dir: Path = Path("media/thumbnails")
    cluster_cache_file: Path = Path("media/cache/face_clusterer.pkl")
    thumbnail_heights: list[int] = [240, 480, 1080]
    web_video_height: int = 1080
    photo_suffixes: tuple[str, ...] = (
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
    def image_suffixes(self) -> tuple[str, ...]:
        return self.photo_suffixes + self.video_suffixes


app_config = AppConfig()

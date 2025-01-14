from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from app.config.config_types import CaptionerProvider, LLMProvider


class AppConfig(BaseSettings):
    # todo make this secure
    password_secret: str = "3df8944bf8afe568d4f0011db0d7fe1ef724f12227b6254116d128caf8c3bee5"  # noqa: S105

    disable_processing: bool = False
    debug: bool = True
    host_thumbnails: bool = True
    connection_string: str = "postgresql+asyncpg://postgres:flyingsquirrel@localhost/photos"
    media_languages: tuple[str, ...] = ("nld", "eng")

    captions_provider: CaptionerProvider = CaptionerProvider.BLIP
    llm_provider: LLMProvider = LLMProvider.MINICPM
    enable_text_summary: bool = Field(
        default=False,
        description="A text summary can be generate of an image or video with an LLM, "
        "improving search capabilities."
        "This operation requires a CUDA gpu and can take a lot of time "
        "if a local LLM is used.",
    )
    enable_document_summary: bool = Field(
        default=False,
        description="If a document is detected, a summary can be made using an LLM. "
        "This operation requires a CUDA gpu and can take a lot of time "
        "if a local LLM is used.",
    )
    document_detection_threshold: int = Field(
        default=65,
        description="How many characters should be recognized before classifying "
        "it as a document and making a summary.",
    )
    face_detection_threshold: float = Field(
        default=0.7,
        description="The minimum confidence threshold for detecting a face. "
        "Values should be between 0 and 1. Higher values mean higher "
        "confidence in the detection.",
    )

    images_dir: Path = Path("media/images")
    thumbnails_dir: Path = Path("media/thumbnails")
    thumbnail_heights: tuple[int, ...] = (200, 250, 300, 400, 500, 750, 1080)
    video_screenshot_percentages: tuple[int, ...] = (1, 33, 66, 95)
    web_video_height_and_quality: tuple[tuple[int, int], ...] = ((360, 40), (1080, 35))
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

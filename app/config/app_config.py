from pathlib import Path

from media_analyzer import AnalyzerSettings, CaptionerProvider, LLMProvider
from media_analyzer.data.enums.analyzer_module import FileModule, VisualModule
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    # todo make this secure
    password_secret: str = "3df8944bf8afe568d4f0011db0d7fe1ef724f12227b6254116d128caf8c3bee5"  # noqa: S105

    disable_processing: bool = False
    debug: bool = True
    host_thumbnails: bool = True
    connection_string: str = "postgresql+asyncpg://postgres:flyingsquirrel@localhost/photos"

    analyzer_settings: AnalyzerSettings = AnalyzerSettings(
        media_languages=("nld", "eng"),
        captions_provider=CaptionerProvider.BLIP,
        llm_provider=LLMProvider.MINICPM,
        enable_text_summary=False,
        enable_document_summary=False,
        document_detection_threshold=65,
        face_detection_threshold=0.7,
        enabled_file_modules={
            FileModule.DATA_URL,
            FileModule.EXIF,
            FileModule.GPS,
            FileModule.TIME,
            FileModule.TAGS,
            FileModule.WEATHER,
        },
        enabled_visual_modules={
            VisualModule.CAPTION,
            VisualModule.CLASSIFICATION,
            VisualModule.EMBEDDING,
            VisualModule.FACES,
            VisualModule.OBJECTS,
            VisualModule.OCR,
            VisualModule.QUALITY_DETECTION,
            VisualModule.SUMMARY,
        },
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

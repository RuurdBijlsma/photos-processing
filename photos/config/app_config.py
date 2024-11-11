from pathlib import Path

from pydantic_settings import BaseSettings


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

    images_dir: Path = Path("data/images")
    thumbnails_dir: Path = Path("data/thumbnails")
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

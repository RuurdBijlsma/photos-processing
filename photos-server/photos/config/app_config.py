from pathlib import Path

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    debug: bool = True
    photos_dir: Path = Path("../data/photos")
    thumbnails_dir: Path = Path("../data/thumbnails")
    thumbnail_sizes: list[int] = [240, 480, 1080]
    host_thumbnails: bool = True
    connection_string: str = "postgresql://postgres:flyingsquirrel@localhost/photos"


app_config = AppConfig()

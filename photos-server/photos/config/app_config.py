from pathlib import Path

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    debug: bool = True
    photos_dir: Path = Path("../data/photos")
    thumbnails_dir: Path = Path("../data/thumbnails")
    host_thumbnails: bool = True
    connection_string: str = "postgresql://postgres:flyingsquirrel@localhost/photos"


app_config = AppConfig()

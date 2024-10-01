from pathlib import Path

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    debug: bool = True
    photos_dir: Path = Path("../data/photos")


app_config = AppConfig()

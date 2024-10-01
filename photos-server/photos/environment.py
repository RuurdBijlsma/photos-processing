from pathlib import Path

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    photos_dir: Path = Path()
    connection_string: str = ""


app_config = AppConfig()

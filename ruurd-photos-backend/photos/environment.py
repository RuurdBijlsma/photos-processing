from pathlib import Path

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    debug: bool = False
    photos_dir: Path = Path()
    thumbnails_dir: Path = Path()
    thumbnail_sizes: list[int] = []
    image_suffixes: tuple[str, ...] = ()
    connection_string: str = ""

    class Config:
        env_file = "config/.env", "config/.env.dev"


app_config = AppConfig()
print(app_config)

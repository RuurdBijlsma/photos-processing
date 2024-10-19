import asyncio
import os
from pathlib import Path

from parsed_ffmpeg import run_ffmpeg, FfmpegError

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.interfaces import BaseImageInfo


async def generate_web_video(input_file: Path, height: int, folder: Path) -> None:
    out_file = folder / "vid.webm"

    await run_ffmpeg(
        [
            "ffmpeg",
            "-i",
            input_file,
            "-c:v",
            "libvpx-vp9",
            "-vf",
            f"scale=-1:{height}",
            "-c:a",
            "libopus",
            out_file,
        ],
        overwrite_output=True,
        print_progress_bar=True,
        progress_bar_description=f"{input_file.name} -> webm",
    )


async def ffmpeg_thumbnails(input_file: Path, sizes: list[int], folder: Path) -> None:
    output_files = [folder / f"{height}p.avif" for height in sizes]
    for out_file, height in zip(output_files, sizes):
        if out_file.exists() and out_file.stat().st_size > 0:
            continue
        while True:
            try:
                await run_ffmpeg(
                    command=[
                        "ffmpeg",
                        "-i",
                        input_file,
                        "-vf",
                        f"scale=-1:{height}",
                        "-vframes",
                        "1",
                        "-map_metadata",
                        "-1",
                        "-qscale:v",
                        "2",
                        out_file,
                    ],
                    overwrite_output=True,
                )
                break
            except FfmpegError as e:
                if "Cannot allocate memory" in str(e):
                    print("ffmpeg memory error, trying again...")
                    await asyncio.sleep(1)
                    continue
                else:
                    raise e


async def generate_thumbnails(image_info: BaseImageInfo) -> None:
    folder = process_config.thumbnails_dir / image_info.hash
    if not os.path.exists(folder):
        os.makedirs(folder)
    input_file = app_config.photos_dir / image_info.relative_path

    await ffmpeg_thumbnails(input_file, process_config.thumbnail_sizes, folder)
    if image_info.relative_path.suffix in process_config.video_suffixes:
        await generate_web_video(input_file, process_config.web_video_height, folder)

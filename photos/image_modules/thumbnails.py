import os
from pathlib import Path
from subprocess import Popen

import ffmpeg  # type: ignore

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.interfaces import BaseImageInfo


def generate_ffmpeg_thumbnails(image_info: BaseImageInfo, sizes: list[int], folder: Path) -> None:
    input_file = app_config.photos_dir / image_info.relative_path
    output_files = [os.path.join(folder, f"{height}p.avif") for height in sizes]
    processes: list[Popen] = []
    for out_file, height in zip(output_files, sizes):
        process = (ffmpeg
                   .input(input_file)
                   .filter('scale', -1, height)
                   .output(out_file, vframes=1)
                   .overwrite_output()
                   .run_async(quiet=True))
        processes.append(process)
    for process in processes:
        process.wait()


def generate_thumbnails(image_info: BaseImageInfo) -> None:
    folder = process_config.thumbnails_dir / image_info.id
    if not os.path.exists(folder):
        os.makedirs(folder)

    generate_ffmpeg_thumbnails(image_info, process_config.thumbnail_sizes, folder)

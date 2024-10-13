import os
from pathlib import Path
from subprocess import Popen

import ffmpeg

from photos.config.app_config import app_config
from photos.config.process_config import process_config
from photos.interfaces import BaseImageInfo


def generate_web_video(input_file: Path, height: int, folder: Path) -> None:
    out_file = folder / "vid.webm"
    (
        ffmpeg.input(input_file)
        .filter("scale", -1, height)
        .output(
            str(out_file),
            vcodec="libvpx-vp9",
            acodec="libopus",
            video_bitrate="2M",
            map_metadata=-1,
        )
        .overwrite_output()
        .run(capture_stdout=False, capture_stderr=True)
    )


def ffmpeg_thumbnails(input_file: Path, sizes: list[int], folder: Path) -> None:
    output_files = [folder / f"{height}p.avif" for height in sizes]
    processes: list[Popen[str]] = []
    for out_file, height in zip(output_files, sizes):
        process = (
            ffmpeg.input(input_file)
            .filter("scale", -1, height)
            .output(str(out_file), vframes=1, map_metadata=-1, qscale=2)
            .overwrite_output()
            .run_async(pipe_stdout=False, pipe_stderr=True)
        )
        processes.append(process)
    for process in processes:
        process.wait()


def generate_thumbnails(image_info: BaseImageInfo) -> None:
    folder = process_config.thumbnails_dir / image_info.id
    if not os.path.exists(folder):
        os.makedirs(folder)
    input_file = app_config.photos_dir / image_info.relative_path

    ffmpeg_thumbnails(input_file, process_config.thumbnail_sizes, folder)
    if image_info.relative_path.suffix in process_config.video_suffixes:
        generate_web_video(input_file, process_config.web_video_height, folder)

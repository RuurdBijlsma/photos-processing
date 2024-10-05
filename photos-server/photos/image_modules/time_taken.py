from datetime import datetime

from photos.interfaces import ExifImageInfo, TimeImageInfo


def get_time_taken(image_info: ExifImageInfo) -> TimeImageInfo:
    return TimeImageInfo(
        **image_info.model_dump(),
        timezone=0,
        time_taken_gmt=datetime.now()
    )

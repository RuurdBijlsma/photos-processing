from collections import defaultdict
from typing import Any

import piexif
from PIL.ExifTags import TAGS
from PIL.ImageFile import ImageFile

from photos.interfaces import BaseImageInfo, ExifImageInfo


def get_all_exif(exif_dict: dict[str, Any]) -> dict[str, dict[str, Any]]:
    all_exif: defaultdict[str, dict[str, Any]] = defaultdict(dict)

    # Loop over the different IFD (Image File Directory) sections
    for ifd in exif_dict:
        if ifd == "0th":
            section_name = "Image"
        elif ifd == "Exif":
            section_name = "EXIF"
        elif ifd == "GPS":
            section_name = "GPS"
        elif ifd == "1st":
            section_name = "Thumbnail"
        else:
            section_name = ifd

        if not isinstance(exif_dict[ifd], dict):
            continue
        for tag, value in exif_dict[ifd].items():
            # Convert the tag number to human-readable name if possible
            tag_name = TAGS.get(tag, tag)
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")
                except UnicodeDecodeError:
                    # Ignore value if it can't be turned into string
                    continue
            all_exif[section_name][tag_name] = value

    return dict(all_exif)


def get_exif(img: ImageFile, image_info: BaseImageInfo) -> ExifImageInfo:
    if "exif" not in img.info:
        exif_data = None
    else:
        exif_data = get_all_exif(piexif.load(img.info["exif"]))
    img_format = img.format if img.format is not None else "UNKNOWN"

    return ExifImageInfo(
        **image_info.model_dump(),
        width=img.width,
        height=img.height,
        format=img_format,
        exif=exif_data,
    )

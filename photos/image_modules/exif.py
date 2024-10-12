from collections import defaultdict
from typing import Any

from PIL.ExifTags import TAGS
from exiftool import ExifToolHelper

from photos.config.app_config import app_config
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


def structure_exiftool_dict(exiftool_dict: dict[str, Any]) -> dict[str, Any]:
    """Exiftool keys are structured as 'File:FileName'.

    This function transforms that to a nested dict."""
    del exiftool_dict["SourceFile"]
    del exiftool_dict["File:Directory"]
    nested_dict = {}

    for key, value in exiftool_dict.items():
        if (
            isinstance(value, str)
            and "(Binary data" in value
            and "use -b option" in value
        ):
            continue  # Ignore binary data keys

        key_parts = key.split(":")

        if len(key_parts) == 1:
            nested_dict[key] = value
        else:
            current_level = nested_dict
            for part in key_parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            current_level[key_parts[-1]] = value

    return nested_dict


def get_exif(image_info: BaseImageInfo) -> ExifImageInfo:
    with ExifToolHelper() as et:
        result = et.execute_json(app_config.photos_dir / image_info.relative_path)
        if (
            result is None
            or not isinstance(result, list)
            or not isinstance(result[0], dict)
        ):
            return ExifImageInfo(
                **image_info.model_dump(),
            )
        exif_dict = structure_exiftool_dict(result[0])

    if "EXIF" in exif_dict:
        alt_ref = exif_dict["EXIF"].get("GPSAltitudeRef")
        # altitude ref = 0 means above sea level
        # ref = 1 means below sea level
        # LG G4 produces ref = 1.8 for some reason when above sea level (maybe also below?)
        if alt_ref != 1 and alt_ref != 0 and alt_ref is not None:
            if "GPSAltitude" in exif_dict["Composite"]:
                exif_dict["Composite"]["GPSAltitude"] = abs(
                    exif_dict["Composite"]["GPSAltitude"]
                )
            exif_dict["EXIF"]["GPSAltitudeRef"] = 0

    assert "ExifTool" in exif_dict
    assert "File" in exif_dict
    assert "Composite" in exif_dict
    width = exif_dict["File"].get("ImageWidth")
    height = exif_dict["File"].get("ImageHeight")
    if width is None:
        width = exif_dict["GIF"]["ImageWidth"]
    if height is None:
        height = exif_dict["GIF"]["ImageHeight"]
    assert width and height
    return ExifImageInfo(
        **image_info.model_dump(),
        size_bytes=exif_dict["File"]["FileSize"],
        width=width,
        height=height,
        format=exif_dict["File"]["MIMEType"],
        exif_tool=exif_dict["ExifTool"],
        file=exif_dict["File"],
        exif=exif_dict.get("EXIF"),
        xmp=exif_dict.get("XMP"),
        jfif=exif_dict.get("JFIF"),
        icc_profile=exif_dict.get("ICC_Profile"),
        composite=exif_dict["Composite"],
        gif=exif_dict.get("GIF"),
    )

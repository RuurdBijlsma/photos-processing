from collections import defaultdict
from typing import Any

from exiftool import ExifToolHelper
from PIL.ExifTags import TAGS

from app.config.app_config import app_config
from app.data.interfaces.image_data import ExifData, ImageData
from app.processing.pipeline.base_module import FileModule


def parse_duration(duration_str: str) -> float:
    h, m, s = duration_str.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def get_all_exif(exif_dict: dict[str, Any]) -> dict[str, dict[str, Any]]:
    all_exif: defaultdict[str, dict[str, Any]] = defaultdict(dict)

    # Loop over the different IFD (Image File Directory) sections
    for ifd, ifd_data in exif_dict.items():
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

        if not isinstance(ifd_data, dict):
            continue
        for tag, value in ifd_data.items():
            # Convert the tag number to human-readable name if possible
            tag_name = TAGS.get(tag, tag)
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")  # noqa: PLW2901
                except UnicodeDecodeError:
                    # Ignore value if it can't be turned into string
                    continue
            all_exif[section_name][tag_name] = value

    return dict(all_exif)


def structure_exiftool_dict(exiftool_dict: dict[str, Any]) -> dict[str, Any]:
    """Exiftool keys are structured as 'File:FileName'.

    This function transforms that to a nested dict.
    """
    del exiftool_dict["SourceFile"]
    del exiftool_dict["File:Directory"]
    nested_dict = {}

    for key, value in exiftool_dict.items():
        if isinstance(value, str) and "(Binary data" in value and "use -b option" in value:
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


class ExifModule(FileModule):
    def process(self, data: ImageData) -> ExifData:
        with ExifToolHelper() as et:
            result = et.execute_json(app_config.images_dir / data.relative_path)
            if result is None or not isinstance(result, list) or not isinstance(result[0], dict):
                raise ValueError(
                    f"Exiftool can't handle this file {data.relative_path}.",
                )
            exif_dict = structure_exiftool_dict(result[0])

        if "EXIF" in exif_dict:
            alt_ref = exif_dict["EXIF"].get("GPSAltitudeRef")
            # altitude ref = 0 means above sea level
            # ref = 1 means below sea level
            # LG G4 produces ref = 1.8 for some reason when above sea level
            #   (maybe also below?)
            if alt_ref not in {0, 1, None}:
                if "GPSAltitude" in exif_dict["Composite"]:
                    exif_dict["Composite"]["GPSAltitude"] = abs(
                        exif_dict["Composite"]["GPSAltitude"],
                    )
                exif_dict["EXIF"]["GPSAltitudeRef"] = 0

        assert "ExifTool" in exif_dict
        assert "File" in exif_dict
        assert "Composite" in exif_dict
        width = exif_dict["File"].get("ImageWidth")
        height = exif_dict["File"].get("ImageHeight")
        duration: float | None = None
        if "GIF" in exif_dict:
            width = exif_dict["GIF"]["ImageWidth"]
            height = exif_dict["GIF"]["ImageHeight"]
        if "QuickTime" in exif_dict:
            duration = exif_dict["QuickTime"]["Duration"]
            width = exif_dict["QuickTime"]["ImageWidth"]
            height = exif_dict["QuickTime"]["ImageHeight"]
        if "Matroska" in exif_dict:
            width = exif_dict["Matroska"]["ImageWidth"]
            height = exif_dict["Matroska"]["ImageHeight"]
            duration = parse_duration(exif_dict["Matroska"]["Duration"])
        assert width and height
        return ExifData(
            **data.model_dump(),
            size_bytes=exif_dict["File"]["FileSize"],
            width=width,
            height=height,
            duration=duration,
            format=exif_dict["File"]["MIMEType"],
            exif_tool=exif_dict["ExifTool"],
            file=exif_dict["File"],
            exif=exif_dict.get("EXIF"),
            xmp=exif_dict.get("XMP"),
            jfif=exif_dict.get("JFIF"),
            icc_profile=exif_dict.get("ICC_Profile"),
            composite=exif_dict["Composite"],
            gif=exif_dict.get("GIF"),
            quicktime=exif_dict.get("QuickTime"),
            matroska=exif_dict.get("Matroska"),
            is_motion_photo=False,
            is_hdr=False,
            is_night_sight=False,
            is_selfie=False,
            is_panorama=False,
        )

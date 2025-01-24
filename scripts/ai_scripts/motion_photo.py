import mimetypes
import mmap
from pathlib import Path
import exiftool
from dataclasses import dataclass


@dataclass
class EmbeddedFile:
    name: str
    mimetype: str
    file_extension: str
    offset: int
    length: int


def extract_slice(input_file: Path, output_file: Path, offset: int, length: int) -> None:
    """
    Extract a slice of the file from the given offset and length, and save it as a separate file.

    Args:
        input_file: Path to the input file to extract data from.
        output_file: Path to the output file where the data slice will be written.
        offset: Byte offset where the slice starts.
        length: Length of the slice to extract.
    """
    try:
        with open(input_file, "rb") as f:
            # Memory-map the file, size 0 means the entire file
            mapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            data_slice = mapped_file[offset: offset + length]

            # Write the extracted slice to the output file
            with open(output_file, "wb") as out_f:
                out_f.write(data_slice)

            mapped_file.close()
    except Exception as e:
        print(f"Error extracting slice from {input_file}: {e}")


def extract_embedded_files(image_path: Path) -> list[EmbeddedFile]:
    """
    Extract embedded files (image/video) from the motion photo.

    This function uses ExifTool to retrieve embedded file metadata and returns
    a list of `EmbeddedFile` instances containing information about each embedded file.

    Args:
        image_path: Path to the image file (motion photo).

    Returns:
        A list of `EmbeddedFile` instances containing the metadata for each embedded file.
    """

    with exiftool.ExifToolHelper() as et:
        result = et.execute_json(str(image_path))[0]

    # Calculate the directory lengths: remaining file size minus embedded lengths
    total_size = result["File:FileSize"]
    embedded_lengths = result["XMP:DirectoryItemLength"]
    remaining_size = total_size - sum(embedded_lengths)
    dir_lengths = [remaining_size] + embedded_lengths

    embedded_files = []
    offset = 0
    for name, mime, length in zip(
            result["XMP:DirectoryItemSemantic"],
            result["XMP:DirectoryItemMime"],
            dir_lengths,
    ):
        embedded_files.append(EmbeddedFile(
            name=name,
            mimetype=mime,
            file_extension=mimetypes.guess_extension(mime),
            offset=offset,
            length=length,
        ))

        # Update the offset for the next embedded file
        offset += length + result["XMP:DirectoryItemPadding"]

    return embedded_files


def main():
    """Main function to extract embedded files from a motion photo and save them to disk."""
    image_path = Path(__file__).parents[1] / "imgs/motion.jpg"

    for file in extract_embedded_files(image_path):
        output_path = image_path.parent / (file.name + file.file_extension)
        extract_slice(image_path, output_path, file.offset, file.length)
        print(f"Extracted {file.name}{file.file_extension} to {output_path}")


if __name__ == "__main__":
    main()

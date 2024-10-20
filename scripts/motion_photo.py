import mmap
from pathlib import Path


# Get byte slices from exiftool
# Use this file to extract thumbnail image, hdr gain map, and motion picture mp4 from a pixel photo
def extract_slice(
    input_file: Path, output_file: Path, offset: int, length: int
) -> None:
    with open(input_file, "rb") as f:
        # Memory-map the file, size 0 means whole file
        mapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        # Extract the slice
        data_slice = mapped_file[offset : offset + length]

        # Write the slice to the output file
        with open(output_file, "wb") as out_f:
            out_f.write(data_slice)

        # Close the memory-mapped file
        mapped_file.close()


# Example usage
# Extracts video from pixel motion photos
# HDR gain map:
# offset = 3809938
# length = 106210

extract_slice(Path("img.jpg"), Path("mmap-out.mp4"), 3809938 + 106210, 2571996)
